"""Arvore de conteudo do item 17 — nucleo do parser (PARSER_SPEC §4).

Monta materia -> topico -> subtopico a partir do outline plano de cada
disciplina. Um candidato a marcador so e aceito se for continuacao plausivel
do estado atual ("proximo numero esperado"); e isso que impede numeros de
lei (14.133/2021) de virarem nos da arvore. Titulos saem literais, sem o
numero e sem ponto final; marcadores de retificacao vao para o versioning.
"""
