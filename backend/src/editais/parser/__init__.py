"""Parser de editais: PDF do edital consolidado -> dict que valida contra
referencia/edital.schema.json.

Biblioteca pura (sem banco, sem API). Principio: extrair muito e afirmar
pouco — todo campo de REVISAO sai como rascunho nao revisado.
Spec completa: referencia/PARSER_SPEC.md.
"""
