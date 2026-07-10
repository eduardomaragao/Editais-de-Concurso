import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
REFERENCIA = REPO_ROOT / "referencia"

SCHEMA_PATH = REFERENCIA / "edital.schema.json"
GOLDEN_PATH = REFERENCIA / "pge_al.instance.json"
PDF_PATH = REFERENCIA / "pge_al.pdf"  # ainda nao existe; testes de fumaca pulam


@pytest.fixture(scope="session")
def schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def golden() -> dict:
    return json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))
