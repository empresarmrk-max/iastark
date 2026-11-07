import os
import platform
from datetime import datetime, timezone


def iastark():
    na_nuvem = os.getenv("GITHUB_ACTIONS") == "true"
    agora = datetime.now(timezone.utc)

    print("IASTARK: programa iniciado.")
    print("Python:", platform.python_version())
    print("Executando no GitHub Actions:", na_nuvem)
    print("Data e hora UTC:", agora.isoformat())
    print("Coleta de informações: desativada.")


if __name__ == "__main__":
    iastark()
