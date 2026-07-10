"""Cronograma do Anexo I (PARSER_SPEC §6).

O pymupdf entrega a tabela como linhas soltas: titulo da atividade (as
vezes quebrado em varias linhas, ate uma palavra por linha), depois a
linha de data, depois eventualmente linhas de horario ("Das 10 horas...")
que sao descartadas. O cabecalho da tabela ("Atividade" / "Datas
previstas") se repete na virada de pagina e tambem e descartado.

Limitacao conhecida: quando uma atividade quebra de pagina DEPOIS da sua
data, a continuacao gruda no titulo da atividade seguinte — vai para a
tela de revisao como tudo o mais.

A ordem de palavras-chave para o `tipo` difere da sugerida na spec: foi
recalibrada contra o Anexo I real da PGE/AL (ex.: "recurso" antes de
"gabarito", "locais de prova" antes de "prova objetiva").
"""

import re
import unicodedata
from dataclasses import dataclass, field

RE_INTERVALO_MESMO_MES = re.compile(r"^(\d{1,2})\s+[ae]\s+(\d{1,2})/(\d{1,2})/(\d{4})$")
RE_INTERVALO_DOIS_MESES = re.compile(
    r"^(\d{1,2})/(\d{1,2})\s+[ae]\s+(\d{1,2})/(\d{1,2})/(\d{4})$"
)
RE_DATA_UNICA = re.compile(r"^(\d{1,2})/(\d{1,2})/(\d{4})$")

LINHAS_IGNORADAS = {"Atividade", "Datas previstas", "ANEXO I", "CRONOGRAMA PREVISTO"}

# (palavra-chave normalizada, tipo do schema) — a PRIMEIRA que casar vence.
ORDEM_TIPOS = [
    ("impugna", "impugnacao"),
    ("recurso", "recurso"),
    ("isen", "isencao"),
    ("atendimento especializado", "atendimento_especializado"),
    ("lactante", "atendimento_especializado"),
    ("pagamento", "pagamento"),
    ("inscri", "inscricoes"),
    ("locais de prova", "locais_prova"),
    ("local de prova", "locais_prova"),
    ("gabarito", "resultado_provisorio"),
    ("padrao", "resultado_provisorio"),
    ("resultado final", "resultado_final"),
    ("resultado", "resultado_provisorio"),
    ("prova objetiva", "prova_objetiva"),
    ("discursiva", "provas_discursivas"),
    ("oral", "prova_oral"),
    ("titulos", "titulos"),
    ("convoca", "convocacao"),
]


@dataclass
class CronogramaResultado:
    eventos: list[dict]
    pendencias: list[str] = field(default_factory=list)


def extrair_cronograma(texto_anexo1: str) -> CronogramaResultado:
    eventos: list[dict] = []
    pendencias: list[str] = []
    titulo_acumulado: list[str] = []

    for linha in texto_anexo1.splitlines():
        linha = " ".join(linha.split())
        if not linha or linha in LINHAS_IGNORADAS:
            continue
        if linha.startswith("*"):
            break  # notas de rodape encerram a tabela
        if linha.startswith("Das ") or linha.startswith("dia ("):
            continue  # detalhe de horario da atividade anterior

        datas = _parse_data(linha)
        if datas is None:
            titulo_acumulado.append(linha)
            continue

        titulo = " ".join(titulo_acumulado).strip()
        titulo_acumulado = []
        if not titulo:
            pendencias.append(f"Data sem atividade associada no Anexo I: {linha}")
            continue
        inicio, fim = datas
        eventos.append(
            {
                "tipo": mapear_tipo(titulo),
                "titulo": titulo,
                "inicio": inicio,
                "fim": fim,
                "fonte": "Anexo I",
            }
        )

    if titulo_acumulado:
        pendencias.append(
            "Atividade sem data no fim do Anexo I: " + " ".join(titulo_acumulado)
        )
    return CronogramaResultado(eventos=eventos, pendencias=pendencias)


def mapear_tipo(titulo: str) -> str:
    normalizado = _norm(titulo)
    for chave, tipo in ORDEM_TIPOS:
        if chave in normalizado:
            return tipo
    return "outro"


def _parse_data(linha: str) -> tuple[str, str | None] | None:
    m = RE_INTERVALO_DOIS_MESES.match(linha)
    if m:
        d1, m1, d2, m2, ano = (int(x) for x in m.groups())
        return _iso(ano, m1, d1), _iso(ano, m2, d2)
    m = RE_INTERVALO_MESMO_MES.match(linha)
    if m:
        d1, d2, mes, ano = (int(x) for x in m.groups())
        return _iso(ano, mes, d1), _iso(ano, mes, d2)
    m = RE_DATA_UNICA.match(linha)
    if m:
        dia, mes, ano = (int(x) for x in m.groups())
        return _iso(ano, mes, dia), None
    return None


def _iso(ano: int, mes: int, dia: int) -> str:
    return f"{ano:04d}-{mes:02d}-{dia:02d}"


def _norm(s: str) -> str:
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
