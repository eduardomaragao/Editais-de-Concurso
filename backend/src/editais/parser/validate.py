"""Validacao contra referencia/edital.schema.json (PARSER_SPEC §10).

Draft 2020-12 com checagem de format. Falha de validacao e erro fatal do
parser: rascunho invalido nao e emitido (assemble.parse_edital levanta
DocumentoInvalido).
"""

import json
from functools import lru_cache
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

SCHEMA_PATH = Path(__file__).resolve().parents[4] / "referencia" / "edital.schema.json"


class DocumentoInvalido(Exception):
    def __init__(self, erros: list[str]):
        self.erros = erros
        super().__init__(
            "Documento nao valida contra edital.schema.json:\n" + "\n".join(erros)
        )


@lru_cache(maxsize=1)
def _validador() -> Draft202012Validator:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    return Draft202012Validator(schema, format_checker=FormatChecker())


def erros(documento: dict) -> list[str]:
    return [
        f"{'/'.join(map(str, e.absolute_path)) or '<raiz>'}: {e.message}"
        for e in _validador().iter_errors(documento)
    ]


def validar(documento: dict) -> None:
    """Levanta DocumentoInvalido se o documento nao passar no schema."""
    problemas = erros(documento)
    if problemas:
        raise DocumentoInvalido(problemas)
