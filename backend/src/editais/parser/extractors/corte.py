"""Corte de lei/jurisprudencia — item 16.32 (PARSER_SPEC §5).

Forma relativa ("vigente na data da primeira publicacao deste edital") e
resolvida para edital.publicacao; "primeira publicacao" implica
afetado_por_retificacao=false (retificacao NAO move o corte). Sempre guarda
fonte e trecho literais. Ambiguidade edital vs. DOE: resolve para a data do
edital, mas marca para revisao com as duas candidatas.
"""
