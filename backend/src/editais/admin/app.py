"""Painel admin (Jinja2, servido pelo FastAPI) + API JSON para o app.

Rodar em dev:
    .venv\\Scripts\\python.exe -m uvicorn --factory editais.admin.app:criar_app --port 8123

Mutacoes sao formularios POST com redirect (303); mensagens de erro viajam
na querystring. A API JSON (/api/...) so expoe editais PUBLICADOS — o app
do candidato nunca ve rascunho.
"""

import base64
import os
import secrets
import shutil
from pathlib import Path
from urllib.parse import quote

from fastapi import Depends, FastAPI, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates

from editais.admin import servico
from editais.api import social
from editais.db import DATA_DIR, Base, criar_engine, criar_sessionmaker
from editais.radar.cebraspe import CebraspeFetcher

TEMPLATES_DIR = Path(__file__).parent / "templates"

# A API publica que o app do candidato consome fica aberta; todo o resto
# (painel de revisao, upload, mutacoes, /docs) exige senha de admin.
PREFIXOS_PUBLICOS = ("/api/",)


def _credenciais_admin() -> tuple[str, str | None]:
    """Usuario e senha do admin. Em producao (Postgres via
    EDITAIS_DATABASE_URL) a senha e OBRIGATORIA — sem ela, o painel fica
    fechado. Em dev (SQLite local) cai num fallback comodo."""
    usuario = os.environ.get("EDITAIS_ADMIN_USUARIO", "admin")
    senha = os.environ.get("EDITAIS_ADMIN_SENHA")
    if senha is None and not os.environ.get("EDITAIS_DATABASE_URL"):
        senha = "dev"  # so vale no SQLite local
    return usuario, senha


def _autorizado(request: Request, usuario: str, senha: str) -> bool:
    cabecalho = request.headers.get("Authorization", "")
    if not cabecalho.startswith("Basic "):
        return False
    try:
        recebido = base64.b64decode(cabecalho[6:]).decode("utf-8")
        u, _, s = recebido.partition(":")
    except (ValueError, UnicodeDecodeError):
        return False
    # compare_digest nos dois campos evita vazar tamanho por timing
    return (
        secrets.compare_digest(u, usuario)
        and secrets.compare_digest(s, senha)
    )


def criar_app(engine=None) -> FastAPI:
    engine = engine if engine is not None else criar_engine()
    Base.metadata.create_all(engine)
    SessaoLocal = criar_sessionmaker(engine)

    app = FastAPI(title="Editais — Painel de revisão")
    # O app Flutter (web, em dev) roda em outra porta e consome /api.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

    usuario_admin, senha_admin = _credenciais_admin()

    @app.middleware("http")
    async def exigir_admin(request: Request, call_next):
        caminho = request.url.path
        if caminho.startswith(PREFIXOS_PUBLICOS):
            return await call_next(request)
        # Producao sem senha configurada: fecha o painel por completo.
        if senha_admin is None:
            return PlainTextResponse(
                "Painel indisponível: defina a variável EDITAIS_ADMIN_SENHA.",
                status_code=503,
            )
        if not _autorizado(request, usuario_admin, senha_admin):
            return Response(
                status_code=401,
                headers={"WWW-Authenticate": 'Basic realm="Editais admin"'},
            )
        return await call_next(request)

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

    def _mutar(s, acao, redirect_ok, redirect_erro):
        """Executa a mutacao e COMMITA ANTES do redirect. O commit do
        teardown da dependency roda depois da resposta, e o GET do redirect
        correria contra ele e leria o estado antigo."""
        try:
            acao()
        except servico.ErroRevisao as exc:
            s.rollback()
            return redirect_erro(str(exc))
        s.commit()
        return redirect_ok()

    def _hub(edital_id: int, erro: str | None = None) -> RedirectResponse:
        url = f"/editais/{edital_id}"
        if erro:
            url += f"?erro={quote(erro)}"
        return RedirectResponse(url, status_code=303)

    def _arvore(edital_id: int, erro: str | None = None) -> RedirectResponse:
        url = f"/editais/{edital_id}/conteudo"
        if erro:
            url += f"?erro={quote(erro)}"
        return RedirectResponse(url, status_code=303)

    # --- paginas do painel ---------------------------------------------------

    @app.get("/")
    def lista(request: Request, s=Depends(sessao)):
        return templates.TemplateResponse(
            request, "lista.html", {"editais": servico.listar(s), "travas": servico.travas}
        )

    @app.post("/upload")
    def upload(arquivo: UploadFile, s=Depends(sessao)):
        destino = DATA_DIR / "uploads" / (arquivo.filename or "edital.pdf")
        destino.parent.mkdir(parents=True, exist_ok=True)
        with destino.open("wb") as f:
            shutil.copyfileobj(arquivo.file, f)
        row = servico.importar_pdf(s, destino)
        s.commit()
        return _hub(row.id)

    @app.get("/editais/{edital_id}")
    def hub(request: Request, edital_id: int, erro: str | None = None, s=Depends(sessao)):
        row = servico.obter(s, edital_id)
        return templates.TemplateResponse(
            request,
            "edital.html",
            {"e": row, "doc": row.documento, "travas": servico.travas(row), "erro": erro},
        )

    @app.get("/editais/{edital_id}/conteudo")
    def conteudo(request: Request, edital_id: int, erro: str | None = None, s=Depends(sessao)):
        row = servico.obter(s, edital_id)
        return templates.TemplateResponse(
            request,
            "conteudo.html",
            {"e": row, "materias": _montar_arvore(row.documento["conteudo"]), "erro": erro},
        )

    # --- acoes de revisao ----------------------------------------------------

    @app.post("/editais/{edital_id}/conteudo/{no_id}/titulo")
    def acao_titulo(edital_id: int, no_id: str, titulo: str = Form(...), s=Depends(sessao)):
        row = servico.obter(s, edital_id)
        return _mutar(
            s,
            lambda: servico.editar_titulo(row, no_id, titulo),
            lambda: _arvore(edital_id),
            lambda erro: _arvore(edital_id, erro),
        )

    @app.post("/editais/{edital_id}/conteudo/{no_id}/promover")
    def acao_promover(edital_id: int, no_id: str, s=Depends(sessao)):
        row = servico.obter(s, edital_id)
        return _mutar(
            s,
            lambda: servico.promover(row, no_id),
            lambda: _arvore(edital_id),
            lambda erro: _arvore(edital_id, erro),
        )

    @app.post("/editais/{edital_id}/conteudo/{no_id}/rebaixar")
    def acao_rebaixar(edital_id: int, no_id: str, s=Depends(sessao)):
        row = servico.obter(s, edital_id)
        return _mutar(
            s,
            lambda: servico.rebaixar(row, no_id),
            lambda: _arvore(edital_id),
            lambda erro: _arvore(edital_id, erro),
        )

    @app.post("/editais/{edital_id}/confirmar-arvore")
    def acao_confirmar_arvore(edital_id: int, s=Depends(sessao)):
        row = servico.obter(s, edital_id)
        return _mutar(
            s,
            lambda: servico.confirmar_arvore(row),
            lambda: _hub(edital_id),
            lambda erro: _hub(edital_id, erro),
        )

    @app.post("/editais/{edital_id}/confirmar-corte")
    def acao_confirmar_corte(
        edital_id: int,
        legislacao_ate: str = Form(""),
        jurisprudencia_ate: str = Form(""),
        s=Depends(sessao),
    ):
        row = servico.obter(s, edital_id)
        return _mutar(
            s,
            lambda: servico.confirmar_corte(
                row, legislacao_ate.strip() or None, jurisprudencia_ate.strip() or None
            ),
            lambda: _hub(edital_id),
            lambda erro: _hub(edital_id, erro),
        )

    @app.post("/editais/{edital_id}/confirmar-datas")
    def acao_confirmar_datas(edital_id: int, s=Depends(sessao)):
        row = servico.obter(s, edital_id)
        return _mutar(
            s,
            lambda: servico.confirmar_datas(row),
            lambda: _hub(edital_id),
            lambda erro: _hub(edital_id, erro),
        )

    @app.post("/editais/{edital_id}/radar")
    def acao_radar(edital_id: int, s=Depends(sessao)):
        row = servico.obter(s, edital_id)
        url_banca = row.documento.get("links", {}).get("pagina_banca")
        if not url_banca:
            return _hub(edital_id, "Sem URL da banca no documento — impossível rodar o radar.")
        try:
            servico.rodar_radar(row, CebraspeFetcher(url_banca))
        except Exception as exc:  # rede fora, HTML mudou etc.
            s.rollback()
            return _hub(edital_id, f"Radar falhou: {exc}")
        s.commit()
        return _hub(edital_id)

    @app.post("/editais/{edital_id}/publicar")
    def acao_publicar(edital_id: int, s=Depends(sessao)):
        row = servico.obter(s, edital_id)
        try:
            servico.publicar(row)
        except servico.TravaPublicacao as exc:
            s.rollback()
            return _hub(edital_id, "Publicação travada: " + " ".join(exc.travas))
        s.commit()
        return _hub(edital_id)

    # --- API JSON (consumida pelo app Flutter) -------------------------------

    @app.get("/api/editais")
    def api_lista(s=Depends(sessao)):
        return [
            {
                "slug": r.slug,
                "orgao": r.documento["edital"]["orgao"],
                "cargo": r.documento["edital"]["cargo"],
                "numero": r.documento["edital"]["numero"],
            }
            for r in servico.listar(s)
            if r.publicado
        ]

    @app.get("/api/editais/{slug}")
    def api_edital(slug: str, s=Depends(sessao)):
        row = servico.obter_por_slug(s, slug)
        if row is None or not row.publicado:
            raise HTTPException(status_code=404, detail="Edital não publicado.")
        return row.documento

    app.include_router(social.criar_router(SessaoLocal))

    return app


def _montar_arvore(nos: list[dict]) -> list[dict]:
    """Achatado -> aninhado para o template: materia > topicos > filhos."""
    filhos: dict[str | None, list[dict]] = {}
    for no in nos:
        filhos.setdefault(no["parent_id"], []).append(no)
    for grupo in filhos.values():
        grupo.sort(key=lambda n: n.get("ordem") or 0)

    def montar(no: dict) -> dict:
        return {"no": no, "filhos": [montar(f) for f in filhos.get(no["id"], [])]}

    return [montar(m) for m in filhos.get(None, [])]
