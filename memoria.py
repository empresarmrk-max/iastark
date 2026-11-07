import json
from datetime import datetime, timezone
from pathlib import Path


def salvar_noticias(noticias, caminho="dados/noticias.json", limite=1000):
    arquivo = Path(caminho)
    memoria = []
    if arquivo.exists():
        memoria = json.loads(arquivo.read_text(encoding="utf-8"))
    if not isinstance(memoria, list):
        raise ValueError("O arquivo de memoria tem um formato invalido.")
    if limite < 1:
        raise ValueError("O limite da memoria deve ser positivo.")

    por_link = {}
    for noticia in memoria:
        if not isinstance(noticia, dict) or not all(
            isinstance(noticia.get(campo), str)
            for campo in ("link", "coletado_em")
        ):
            raise ValueError("Existe um registro invalido na memoria.")
        por_link[noticia["link"]] = noticia

    agora = datetime.now(timezone.utc).isoformat()
    novas = 0
    campos = ("titulo", "link", "fonte", "publicado_em")

    for noticia in reversed(noticias):
        link = noticia["link"]
        if not link.startswith(("https://", "http://")):
            raise ValueError("Uma noticia veio sem link valido.")
        if link not in por_link:
            por_link[link] = {"coletado_em": agora}
            novas += 1
        por_link[link].update({campo: noticia[campo] for campo in campos})

    registros = list(por_link.values())[-limite:]
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    temporario = arquivo.with_suffix(".tmp")
    temporario.write_text(
        json.dumps(registros, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporario.replace(arquivo)
    return novas, len(registros)
