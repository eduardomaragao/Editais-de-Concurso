"""Radar de retificacoes (PARSER_SPEC §9).

Monitora o site da banca (fetcher plugavel por banca; Cebraspe primeiro),
compara ultima_retificacao_publicada com retificacoes_incorporadas e marca
radar_desatualizado — que trava a publicacao e pede reupload do consolidado.
Tambem descobre novos editais de interesse. Educado com a banca: cache,
robots.txt, intervalo entre requisicoes.
"""
