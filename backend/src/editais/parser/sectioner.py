"""Divisao do texto em secoes (PARSER_SPEC §3).

Localiza os itens numerados de 1o nivel no inicio de linha e confirma pela
sequencia (1, 2, 3...) para nao confundir com subitens ou numeros soltos de
tabela. Anexos sao ancorados por "ANEXO <romano>" no inicio de linha. Cada
extrator recebe apenas o seu trecho.
"""

import re
from dataclasses import dataclass, field

RE_ANCORA_ITEM = re.compile(r"(?m)^(\d{1,2})\s+([A-ZÀ-Ü].*)$")
RE_ANCORA_ANEXO = re.compile(r"(?m)^ANEXO\s+([IVX]+)\b")


@dataclass
class Secoes:
    preambulo: str  # cabecalho + intro, antes do item 1
    itens: dict[int, str] = field(default_factory=dict)
    anexos: dict[str, str] = field(default_factory=dict)


def dividir(texto: str) -> Secoes:
    ancoras: list[tuple[int, int]] = []  # (numero_do_item, posicao)
    esperado = 1
    for m in RE_ANCORA_ITEM.finditer(texto):
        # Cabecalho de item de 1o nivel e TODO em caixa alta ("16 DAS
        # DISPOSIÇÕES FINAIS"). Sem essa exigencia, um topico do outline do
        # item 17 que caia no inicio de linha ("18 Lei Complementar...")
        # viraria um falso item 18.
        titulo = m.group(2).strip()
        if int(m.group(1)) == esperado and titulo == titulo.upper():
            ancoras.append((esperado, m.start()))
            esperado += 1

    marcas_anexo = list(RE_ANCORA_ANEXO.finditer(texto))
    fim_dos_itens = marcas_anexo[0].start() if marcas_anexo else len(texto)

    itens: dict[int, str] = {}
    for i, (numero, posicao) in enumerate(ancoras):
        fim = ancoras[i + 1][1] if i + 1 < len(ancoras) else fim_dos_itens
        itens[numero] = texto[posicao:fim]

    anexos: dict[str, str] = {}
    for i, m in enumerate(marcas_anexo):
        fim = marcas_anexo[i + 1].start() if i + 1 < len(marcas_anexo) else len(texto)
        anexos[m.group(1)] = texto[m.start() : fim]

    preambulo = texto[: ancoras[0][1]] if ancoras else texto
    return Secoes(preambulo=preambulo, itens=itens, anexos=anexos)
