import os
import sys
import xml.etree.ElementTree as ET
from urllib.request import Request, urlopen
from memoria import salvar_noticias

FEED_URL = "https://agenciabrasil.ebc.com.br/rss/ultimasnoticias/feed.xml"
MAX_BYTES = 2_000_000


def buscar_noticias():
    pedido = Request(
        FEED_URL,
        headers={
            "User-Agent": "IASTARK/0.1",
            "Accept": "application/rss+xml, application/xml, text/xml",
        },
    )
    with urlopen(pedido, timeout=20) as resposta:
        dados = resposta.read(MAX_BYTES + 1)

    if len(dados) > MAX_BYTES:
        raise ValueError("A resposta ultrapassou o limite de 2 MB.")
    if b"<!DOCTYPE" in dados.upper() or b"<!ENTITY" in dados.upper():
        raise ValueError("O feed trouxe uma estrutura XML inesperada.")

    noticias = ET.fromstring(dados).findall("./channel/item")
    if not noticias:
        raise ValueError("A fonte nao retornou noticias em formato RSS.")
    return noticias


def texto(item, campo):
    return " ".join((item.findtext(campo) or "Nao informado").split())


def iastark():
    print("IASTARK: leitor de noticias.")
    autorizado = os.getenv(
        "IASTARK_AUTORIZAR_INTERNET", "false"
    ).strip().lower() == "true"

    if not autorizado:
        print("Consulta de noticias nao autorizada.")
        print("Marque a autorizacao em Run workflow para permitir a consulta.")
        return 0

    print("Autorizacao recebida para esta execucao.")
    print("Consultando o RSS da Agencia Brasil...")

    try:
        noticias = buscar_noticias()
        registros = [
            {
                "titulo": texto(item, "title"),
                "link": texto(item, "link"),
                "fonte": "Agencia Brasil",
                "publicado_em": texto(item, "pubDate"),
            }
            for item in noticias
        ]
        novas, total = salvar_noticias(registros)
    except (OSError, ET.ParseError, ValueError) as erro:
        print(f"Falha ao consultar ou preparar a memoria: {erro}", file=sys.stderr)
        return 1

    for numero, item in enumerate(noticias[:5], start=1):
        print(f"\n{numero}. {texto(item, 'title')}")
        print("Publicado:", texto(item, "pubDate"))
        print("Link:", texto(item, "link"))

    print(f"\nConsulta concluida: {len(noticias)} noticias recebidas.")
    print(f"Novas na memoria: {novas}. Total no arquivo: {total}.")
    print("Arquivo preparado: dados/noticias.json")
    return 0


if __name__ == "__main__":
    sys.exit(iastark())
