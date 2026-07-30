#!/usr/bin/env python3
"""Baixa os informativos do STF listados na página "Edições Anteriores".

Rodar na SUA máquina (o ambiente remoto não alcança o site do STF).
Só usa a biblioteca padrão — não precisa instalar nada.

Uso (PowerShell, dentro de informativos/stf/):

    python baixar.py --listar        # 1º passo: mostra o que encontrou, sem baixar
    python baixar.py                 # baixa tudo (nº >= 1050 ~ 2023+) para brutos/
    python baixar.py --min 1080 --max 1300

    python baixar.py --padrao --min 1080 --max 1200
                                     # modo direto: nao le a listagem, monta a
                                     # URL de cada edicao pelo numero e tenta
                                     # os formatos em ordem (docx, doc, htm...).
                                     # É o mais robusto quando a listagem muda.

    python baixar.py --pagina "Edicoes_Anteriores.html"
                                     # plano B: se o site bloquear o script,
                                     # salve a listagem no navegador (Ctrl+S)
                                     # e aponte o arquivo salvo aqui

Preferência de formato por edição: docx > doc > rtf > htm/html > pdf.
Arquivos já baixados são pulados (dá para retomar).
"""

import argparse
import re
import sys
import time
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit

URL_LISTAGEM = (
    "https://portal.stf.jus.br/textos/verTexto.asp"
    "?servico=informativoSTF&pagina=Edicoes_Anteriores"
)
CABECALHOS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9",
}
EXTENSOES = (".docx", ".doc", ".rtf", ".pdf", ".htm", ".html")
PRIORIDADE = {".docx": 0, ".doc": 1, ".rtf": 2, ".htm": 3, ".html": 3, ".pdf": 4}
PAUSA_SEGUNDOS = 1.5
MAX_PAGINAS_INTERMEDIARIAS = 80


def pausar():
    if PAUSA_SEGUNDOS > 0:
        time.sleep(PAUSA_SEGUNDOS)


def buscar(url: str) -> bytes:
    ultimo_erro = None
    for espera in (0, 2, 4, 8):
        if espera:
            time.sleep(espera)
        try:
            requisicao = urllib.request.Request(url, headers=CABECALHOS)
            with urllib.request.urlopen(requisicao, timeout=60) as resposta:
                return resposta.read()
        except (urllib.error.URLError, OSError) as erro:
            ultimo_erro = erro
    raise RuntimeError(f"falha ao buscar {url}: {ultimo_erro}")


class ColetorDeLinks(HTMLParser):
    """Coleta pares (href, texto do link) de uma página."""

    def __init__(self):
        super().__init__()
        self.links = []
        self._href = None
        self._texto = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self._href = dict(attrs).get("href")
            self._texto = []

    def handle_data(self, data):
        if self._href is not None:
            self._texto.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self._href is not None:
            texto = " ".join(" ".join(self._texto).split())
            self.links.append((self._href.strip(), texto))
            self._href = None
            self._texto = []


def extrair_links(html: bytes, url_base: str):
    try:
        texto = html.decode("utf-8")
    except UnicodeDecodeError:
        texto = html.decode("latin-1")
    coletor = ColetorDeLinks()
    coletor.feed(texto)
    resultado = []
    for href, rotulo in coletor.links:
        if not href or href.startswith(("javascript:", "mailto:", "#")):
            continue
        resultado.append((urljoin(url_base, href), rotulo))
    return resultado


def numero_da_edicao(url: str, rotulo: str):
    """Tenta descobrir o nº do informativo pelo nome do arquivo ou pelo texto."""
    nome = Path(urlsplit(url).path).name
    for fonte in (nome, rotulo, url):
        m = re.search(r"informativo\D{0,10}(\d{1,2}\.?\d{3}|\d{3,4})", fonte, re.I)
        if m:
            return int(m.group(1).replace(".", ""))
    m = re.search(r"\b(\d{1,2}\.?\d{3}|\d{3,4})\b", rotulo)
    if m:
        n = int(m.group(1).replace(".", ""))
        if n < 2000:  # evita confundir com ano (2023, 2024...)
            return n
    return None


def eh_documento(url: str) -> bool:
    return urlsplit(url).path.lower().endswith(EXTENSOES)


def parece_informativo(url: str, rotulo: str) -> bool:
    alvo = (url + " " + rotulo).lower()
    return "informativo" in alvo


def coletar(html_listagem: bytes, url_base: str, minimo: int, maximo):
    """Retorna {numero: [(prioridade, url, rotulo), ...]} e links não identificados."""
    links = extrair_links(html_listagem, url_base)
    documentos = []
    intermediarias = []
    for url, rotulo in links:
        if eh_documento(url):
            documentos.append((url, rotulo))
        elif parece_informativo(url, rotulo):
            n = numero_da_edicao(url, rotulo)
            if n is not None and n >= minimo and (maximo is None or n <= maximo):
                intermediarias.append((url, rotulo, n))

    # Páginas intermediárias: edições cujo link é uma página .asp que contém
    # o arquivo de verdade (Word/PDF) dentro dela.
    vistas = set()
    for url, rotulo, n in intermediarias[:MAX_PAGINAS_INTERMEDIARIAS]:
        if url in vistas:
            continue
        vistas.add(url)
        print(f"  .. abrindo pagina da edicao {n}: {url}")
        pausar()
        try:
            html = buscar(url)
        except RuntimeError as erro:
            print(f"     (falhou: {erro})")
            continue
        for url_doc, rotulo_doc in extrair_links(html, url):
            if eh_documento(url_doc):
                documentos.append((url_doc, rotulo_doc or rotulo))

    if len(intermediarias) > MAX_PAGINAS_INTERMEDIARIAS:
        print(
            f"AVISO: {len(intermediarias)} paginas intermediarias encontradas; "
            f"abrindo so as {MAX_PAGINAS_INTERMEDIARIAS} primeiras. "
            "Rode de novo com --min maior para pegar o resto."
        )

    por_numero = {}
    sem_numero = []
    for url, rotulo in documentos:
        n = numero_da_edicao(url, rotulo)
        ext = Path(urlsplit(url).path).suffix.lower()
        prioridade = PRIORIDADE.get(ext, 9)
        if n is None:
            sem_numero.append((url, rotulo))
        elif n >= minimo and (maximo is None or n <= maximo):
            por_numero.setdefault(n, []).append((prioridade, url, rotulo))
    return por_numero, sem_numero


# Padroes de URL ja usados pelo STF para o arquivo de cada edicao.
# {n} = numero do informativo. Ordem = preferencia de formato.
PADROES_URL = (
    "https://portal.stf.jus.br/arquivo/informativo/documento/informativo{n}.docx",
    "https://www.stf.jus.br/arquivo/informativo/documento/informativo{n}.docx",
    "https://portal.stf.jus.br/arquivo/informativo/documento/informativo{n}.doc",
    "https://portal.stf.jus.br/arquivo/informativo/documento/informativo{n}.htm",
    "https://www.stf.jus.br/arquivo/informativo/documento/informativo{n}.htm",
    "https://portal.stf.jus.br/arquivo/informativo/documento/informativo{n}.pdf",
    "https://www.stf.jus.br/arquivo/informativo/documento/informativo{n}.pdf",
)


def tentar_uma_vez(url: str) -> bytes:
    """Como buscar(), mas sem retry — para sondar se a URL existe."""
    requisicao = urllib.request.Request(url, headers=CABECALHOS)
    with urllib.request.urlopen(requisicao, timeout=60) as resposta:
        return resposta.read()


def baixar_por_padrao(destino: Path, minimo: int, maximo: int, apenas_listar: bool):
    """Monta a URL de cada edicao pelo numero, sem depender da listagem."""
    destino.mkdir(parents=True, exist_ok=True)
    baixados = pulados = falhas = 0
    for n in range(minimo, maximo + 1):
        ja = sorted(destino.glob(f"informativo-{n}.*"))
        if any(a.stat().st_size > 0 for a in ja):
            pulados += 1
            continue
        conteudo = None
        origem = None
        for modelo in PADROES_URL:
            url = modelo.format(n=n)
            try:
                pausar()
                dados = tentar_uma_vez(url)
            except (urllib.error.URLError, OSError):
                continue
            if dados and len(dados) > 2000:  # descarta pagina de erro curta
                conteudo, origem = dados, url
                break
        if conteudo is None:
            print(f"informativo {n}: nao encontrado em nenhum formato")
            falhas += 1
            continue
        ext = Path(urlsplit(origem).path).suffix.lower()
        arquivo = destino / f"informativo-{n}{ext}"
        print(f"informativo {n}: {origem} -> {arquivo.name} ({len(conteudo)//1024} KB)")
        if not apenas_listar:
            arquivo.write_bytes(conteudo)
        baixados += 1
    print(f"\nPronto: {baixados} baixados, {pulados} ja existiam, {falhas} nao achados.")
    if falhas:
        print(
            "Os 'nao achados' podem ser numeros que nao existem ou que usam outro\n"
            "padrao de URL. Rode com --listar para conferir na listagem oficial."
        )


def principal():
    global PAUSA_SEGUNDOS
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--listar", action="store_true", help="so mostra, nao baixa")
    parser.add_argument("--min", type=int, default=1050, help="menor nº (padrao 1050)")
    parser.add_argument("--max", type=int, default=None, help="maior nº (padrao: sem limite)")
    parser.add_argument("--pagina", help="arquivo HTML salvo da listagem (plano B)")
    parser.add_argument(
        "--padrao",
        action="store_true",
        help="ignora a listagem e monta a URL de cada edicao pelo numero",
    )
    parser.add_argument(
        "--pausa",
        type=float,
        default=PAUSA_SEGUNDOS,
        help=f"segundos entre requisicoes (padrao {PAUSA_SEGUNDOS})",
    )
    parser.add_argument("--url", default=URL_LISTAGEM, help="URL da listagem")
    parser.add_argument(
        "--destino", default=str(Path(__file__).parent / "brutos"), help="pasta de saida"
    )
    args = parser.parse_args()
    PAUSA_SEGUNDOS = args.pausa

    if args.padrao:
        if args.max is None:
            parser.error("--padrao precisa de --max (ex.: --min 1080 --max 1200)")
        baixar_por_padrao(Path(args.destino), args.min, args.max, args.listar)
        return

    if args.pagina:
        html = Path(args.pagina).read_bytes()
        print(f"Lendo listagem salva: {args.pagina}")
    else:
        print(f"Buscando listagem: {args.url}")
        html = buscar(args.url)

    por_numero, sem_numero = coletar(html, args.url, args.min, args.max)

    if not por_numero and not sem_numero:
        print(
            "\nNenhum arquivo de informativo encontrado na listagem.\n"
            "Plano B: abra a pagina no navegador, salve com Ctrl+S\n"
            "('Pagina da web, somente HTML') e rode:\n"
            "    python baixar.py --pagina \"arquivo salvo.html\"\n"
            "Se ainda assim nao achar nada, me mande o arquivo salvo que eu\n"
            "ajusto o script."
        )
        sys.exit(1)

    escolhidos = {n: min(opcoes) for n, opcoes in sorted(por_numero.items())}
    print(f"\nEdicoes encontradas (nº {args.min}+): {len(escolhidos)}")
    for n, (_, url, _) in escolhidos.items():
        print(f"  informativo {n}: {url}")
    if sem_numero:
        print(f"\nLinks de arquivo sem numero identificado ({len(sem_numero)}):")
        for url, rotulo in sem_numero:
            print(f"  {rotulo or '(sem texto)'}: {url}")

    if args.listar:
        print("\n(--listar: nada foi baixado)")
        return

    destino = Path(args.destino)
    destino.mkdir(parents=True, exist_ok=True)
    baixados = pulados = falhas = 0
    for n, (_, url, _) in escolhidos.items():
        ext = Path(urlsplit(url).path).suffix.lower() or ".html"
        arquivo = destino / f"informativo-{n}{ext}"
        if arquivo.exists() and arquivo.stat().st_size > 0:
            pulados += 1
            continue
        print(f"Baixando informativo {n} -> {arquivo.name}")
        pausar()
        try:
            arquivo.write_bytes(buscar(url))
            baixados += 1
        except RuntimeError as erro:
            print(f"  FALHOU: {erro}")
            falhas += 1

    print(
        f"\nPronto: {baixados} baixados, {pulados} ja existiam, {falhas} falharam."
    )
    if falhas:
        print("Rode o script de novo para tentar so os que falharam.")


if __name__ == "__main__":
    principal()
