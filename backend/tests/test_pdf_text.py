"""Unidades do pdf_text.py (a parte que nao depende do PDF real)."""

from editais.parser import pdf_text


def test_de_hifenizar_palavra_partida_remove_o_hifen():
    assert pdf_text.de_hifenizar("respon-\nsabilidade civil") == "responsabilidade civil"


def test_de_hifenizar_composto_mantem_o_hifen():
    assert pdf_text.de_hifenizar("Procuradoria-\nGeral do Estado") == (
        "Procuradoria-Geral do Estado"
    )


def test_de_hifenizar_nao_cola_item_novo():
    texto = "conforme o subitem 9.7 -\n10 PROVA ORAL"
    assert pdf_text.de_hifenizar(texto) == texto


def test_remover_cabecalho_rodape():
    paginas = [f"ESTADO DE ALAGOAS\nconteudo da pagina {i}\nPagina {i}" for i in range(6)]
    limpas = pdf_text.remover_cabecalho_rodape(paginas)
    assert limpas[2] == "conteudo da pagina 2\nPagina 2"  # rodape varia, fica


def test_remover_cabecalho_nao_mexe_em_documento_curto():
    paginas = ["A\nx", "A\ny", "A\nz"]
    assert pdf_text.remover_cabecalho_rodape(paginas) == paginas


def test_montar_texto_offsets():
    resultado = pdf_text.montar_texto(["abc", "de", "f"])
    assert resultado.texto == "abc\nde\nf"
    assert resultado.offsets_paginas == [0, 4, 7]
    assert resultado.texto[4:6] == "de"
