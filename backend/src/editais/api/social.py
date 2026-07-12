"""API da rede de amigos: comparar progresso e mandar incentivos.

Modelo de conta deliberadamente leve (sem senha): o app registra um apelido,
recebe um `codigo` de amigo (para compartilhar) e um `token` de aparelho
(guardado no dispositivo, enviado no header X-Token). Amizade e mutua: quem
adiciona o codigo do outro vira amigo dos dois lados.

So o RESUMO do progresso sobe (pontos, percentual, nos concluidos) — a arvore
marcada continua no aparelho do candidato.
"""

import re
import secrets

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import or_, select

from editais.db.models import Amizade, Incentivo, ProgressoSync, Usuario

ALFABETO_CODIGO = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"  # sem 0/O/1/I/L

MENSAGEM_MAX = 200


class NovoUsuario(BaseModel):
    apelido: str = Field(min_length=2, max_length=40)


class NovoAmigo(BaseModel):
    codigo: str


class ProgressoEnviado(BaseModel):
    edital: str = Field(min_length=1, max_length=120)
    pontos: int = Field(ge=0)
    percentual: float = Field(ge=0, le=1)
    concluidos: int = Field(ge=0)


class NovoIncentivo(BaseModel):
    codigo: str
    mensagem: str = Field(min_length=1, max_length=MENSAGEM_MAX)
    edital: str | None = None


def criar_router(SessaoLocal) -> APIRouter:
    router = APIRouter(prefix="/api/social", tags=["social"])

    def sessao():
        s = SessaoLocal()
        try:
            yield s
            s.commit()
        except Exception:
            s.rollback()
            raise
        finally:
            s.close()

    def usuario_atual(s=Depends(sessao), x_token: str = Header(alias="X-Token")) -> Usuario:
        usuario = s.scalar(select(Usuario).where(Usuario.token == x_token))
        if usuario is None:
            raise HTTPException(status_code=401, detail="Token inválido.")
        return usuario

    def _por_codigo(s, codigo: str) -> Usuario:
        normalizado = re.sub(r"[^A-Z0-9]", "", codigo.upper())
        usuario = s.scalar(select(Usuario).where(Usuario.codigo == normalizado))
        if usuario is None:
            raise HTTPException(status_code=404, detail="Código de amigo não encontrado.")
        return usuario

    def _amigos_ids(s, usuario: Usuario) -> set[int]:
        linhas = s.scalars(
            select(Amizade).where(
                or_(Amizade.usuario_id == usuario.id, Amizade.amigo_id == usuario.id)
            )
        )
        return {
            l.amigo_id if l.usuario_id == usuario.id else l.usuario_id for l in linhas
        }

    @router.post("/usuarios", status_code=201)
    def registrar(corpo: NovoUsuario, s=Depends(sessao)):
        codigo = "".join(secrets.choice(ALFABETO_CODIGO) for _ in range(6))
        usuario = Usuario(
            apelido=corpo.apelido.strip(),
            codigo=codigo,
            token=secrets.token_urlsafe(24),
        )
        s.add(usuario)
        s.commit()
        return {
            "apelido": usuario.apelido,
            "codigo": usuario.codigo,
            "token": usuario.token,
        }

    @router.post("/amigos", status_code=201)
    def adicionar_amigo(corpo: NovoAmigo, s=Depends(sessao), eu=Depends(usuario_atual)):
        amigo = _por_codigo(s, corpo.codigo)
        if amigo.id == eu.id:
            raise HTTPException(status_code=400, detail="Esse código é o seu!")
        if amigo.id in _amigos_ids(s, eu):
            raise HTTPException(status_code=409, detail="Vocês já são amigos.")
        s.add(Amizade(usuario_id=eu.id, amigo_id=amigo.id))
        s.commit()
        return {"apelido": amigo.apelido, "codigo": amigo.codigo}

    @router.get("/amigos")
    def listar_amigos(edital: str, s=Depends(sessao), eu=Depends(usuario_atual)):
        ids = _amigos_ids(s, eu)
        if not ids:
            return []
        progresso = {
            p.usuario_id: p
            for p in s.scalars(
                select(ProgressoSync).where(
                    ProgressoSync.usuario_id.in_(ids),
                    ProgressoSync.edital_slug == edital,
                )
            )
        }
        amigos = s.scalars(select(Usuario).where(Usuario.id.in_(ids)))
        resposta = []
        for amigo in amigos:
            p = progresso.get(amigo.id)
            resposta.append(
                {
                    "apelido": amigo.apelido,
                    "codigo": amigo.codigo,
                    "pontos": p.pontos if p else 0,
                    "percentual": p.percentual if p else 0.0,
                    "concluidos": p.concluidos if p else 0,
                    "atualizado_em": p.atualizado_em.isoformat() if p else None,
                }
            )
        resposta.sort(key=lambda a: a["pontos"], reverse=True)
        return resposta

    @router.put("/progresso")
    def enviar_progresso(corpo: ProgressoEnviado, s=Depends(sessao), eu=Depends(usuario_atual)):
        linha = s.scalar(
            select(ProgressoSync).where(
                ProgressoSync.usuario_id == eu.id,
                ProgressoSync.edital_slug == corpo.edital,
            )
        )
        if linha is None:
            linha = ProgressoSync(usuario_id=eu.id, edital_slug=corpo.edital)
            s.add(linha)
        linha.pontos = corpo.pontos
        linha.percentual = corpo.percentual
        linha.concluidos = corpo.concluidos
        s.commit()
        return {"ok": True}

    @router.post("/incentivos", status_code=201)
    def enviar_incentivo(corpo: NovoIncentivo, s=Depends(sessao), eu=Depends(usuario_atual)):
        destino = _por_codigo(s, corpo.codigo)
        if destino.id not in _amigos_ids(s, eu):
            raise HTTPException(status_code=403, detail="Vocês ainda não são amigos.")
        s.add(
            Incentivo(
                de_id=eu.id,
                para_id=destino.id,
                mensagem=corpo.mensagem.strip(),
                edital_slug=corpo.edital,
            )
        )
        s.commit()
        return {"ok": True}

    @router.get("/incentivos")
    def receber_incentivos(s=Depends(sessao), eu=Depends(usuario_atual)):
        """Devolve os incentivos nao lidos e ja os marca como lidos."""
        pendentes = list(
            s.scalars(
                select(Incentivo)
                .where(Incentivo.para_id == eu.id, Incentivo.lido == False)  # noqa: E712
                .order_by(Incentivo.criado_em)
            )
        )
        remetentes = {
            u.id: u.apelido
            for u in s.scalars(
                select(Usuario).where(Usuario.id.in_({i.de_id for i in pendentes} or {0}))
            )
        }
        resposta = [
            {
                "de": remetentes.get(i.de_id, "?"),
                "mensagem": i.mensagem,
                "criado_em": i.criado_em.isoformat(),
            }
            for i in pendentes
        ]
        for i in pendentes:
            i.lido = True
        s.commit()
        return resposta

    return router
