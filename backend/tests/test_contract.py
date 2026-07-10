"""O contrato em si: o golden file deve validar contra o schema.

Se este teste quebrar, ou o schema ou o golden mudou de forma incompativel —
resolver antes de mexer no parser.
"""

from jsonschema import Draft202012Validator
from jsonschema import FormatChecker


def test_schema_is_valid_draft_2020_12(schema):
    Draft202012Validator.check_schema(schema)


def test_golden_instance_validates_against_schema(schema, golden):
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = list(validator.iter_errors(golden))
    assert errors == [], "\n".join(
        f"{'/'.join(map(str, e.absolute_path))}: {e.message}" for e in errors
    )


def test_golden_review_flags_start_unreviewed(golden):
    # Regra inviolavel: nada publica sem revisao humana — o golden e um
    # rascunho pos-parser, entao a trava tem que estar fechada.
    assert golden["edital"]["conteudo_revisado"] is False
    assert golden["edital"]["corte_conteudo"]["informado"] is True
