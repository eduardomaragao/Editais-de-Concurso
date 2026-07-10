"""Unidades do sectioner.py (o teste no PDF real esta em test_pdf_smoke.py)."""

from editais.parser import sectioner

DOCUMENTO = """CABECALHO DO EDITAL
EDITAL Nº 1 – PGE/AL, DE 31 DE MARÇO DE 2026
intro do edital.
1 DAS DISPOSIÇÕES PRELIMINARES
1.1 texto do item um.
2 DO CARGO
texto do item dois.
5 e 6/5/2026
3 DOS OBJETOS DE AVALIAÇÃO
DIREITO X: 1 Estado. 17 Controle.
18 Lei Complementar estadual nº 7/1991 (não é item de edital).
ANEXO I
CRONOGRAMA PREVISTO
linhas do anexo um.
ANEXO II
MODELO DE LAUDO
"""


def test_divide_itens_confirmando_sequencia_e_caixa_alta():
    secoes = sectioner.dividir(DOCUMENTO)
    assert sorted(secoes.itens) == [1, 2, 3]
    assert secoes.itens[1].startswith("1 DAS DISPOSIÇÕES PRELIMINARES")
    assert "item dois" in secoes.itens[2]
    # "18 Lei Complementar..." nao vira item (nao e caixa alta) e fica
    # dentro do item 3; "5 e 6/5/2026" tampouco (fora de sequencia).
    assert "18 Lei Complementar" in secoes.itens[3]
    assert "5 e 6/5/2026" in secoes.itens[2]


def test_preambulo_e_anexos():
    secoes = sectioner.dividir(DOCUMENTO)
    assert "EDITAL Nº 1" in secoes.preambulo
    assert sorted(secoes.anexos) == ["I", "II"]
    assert "CRONOGRAMA" in secoes.anexos["I"]
    assert "ANEXO II" not in secoes.anexos["I"]
    assert secoes.anexos["II"].startswith("ANEXO II")


def test_item_final_termina_no_primeiro_anexo():
    secoes = sectioner.dividir(DOCUMENTO)
    assert "ANEXO I" not in secoes.itens[3]
