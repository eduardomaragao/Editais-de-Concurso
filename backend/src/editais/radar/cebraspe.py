"""Fetcher da Cebraspe.

O parse do HTML e separado do download para os testes nao dependerem de
rede. O padrao dos links na pagina do concurso e uma ancora para o PDF com
texto "Edital nº N – ORGAO, de D de MES de AAAA - Descricao".

Educacao com a banca (PARSER_SPEC §9): o servico agendado que usa este
fetcher deve manter cache do HTML, respeitar robots.txt e espacar as
requisicoes — este modulo faz UMA requisicao por chamada, com User-Agent
identificado, e nada de burlar protecao. Se a pagina for dinamica demais,
preferir o indice de arquivos/endpoint estavel da banca.
"""

import re
import urllib.request
from typing import Callable

from editais.parser.util import MESES, norm_ascii
from editais.radar.core import EditalPublicado

USER_AGENT = "EditaisRadar/0.1 (+https://eduardoaragao.com)"

RE_ANCORA = re.compile(
    r"<a[^>]+href=\"([^\"]+\.pdf)\"[^>]*>(.*?)</a>", re.IGNORECASE | re.DOTALL
)
RE_EDITAL_TEXTO = re.compile(
    r"Edital\s+n[ºo°]\s*(\d+)[^,<]*,\s*de\s+(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})",
    re.IGNORECASE,
)


def baixar_html(url: str, timeout: int = 30) -> str:
    requisicao = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(requisicao, timeout=timeout) as resposta:
        return resposta.read().decode("utf-8", errors="replace")


def extrair_editais_do_html(html: str) -> list[EditalPublicado]:
    editais: dict[int, EditalPublicado] = {}
    for url, texto in RE_ANCORA.findall(html):
        texto_limpo = " ".join(re.sub(r"<[^>]+>", " ", texto).split())
        m = RE_EDITAL_TEXTO.search(texto_limpo)
        if m is None:
            continue
        numero = int(m.group(1))
        mes = MESES.get(norm_ascii(m.group(3)))
        data = (
            f"{int(m.group(4)):04d}-{mes:02d}-{int(m.group(2)):02d}" if mes else None
        )
        # a pagina pode listar o mesmo edital mais de uma vez; a ultima vence
        editais[numero] = EditalPublicado(
            numero=numero, data=data, titulo=texto_limpo, url=url
        )
    return [editais[n] for n in sorted(editais)]


class CebraspeFetcher:
    """fetch_editais() para uma pagina de concurso da Cebraspe."""

    def __init__(
        self, url_concurso: str, baixar: Callable[[str], str] = baixar_html
    ):
        self.url_concurso = url_concurso
        self._baixar = baixar

    def fetch_editais(self) -> list[EditalPublicado]:
        return extrair_editais_do_html(self._baixar(self.url_concurso))
