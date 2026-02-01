import os
import requests
import zipfile
from io import BytesIO

# Configurações de acesso
BASE_URL = "https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/"
URL_CADASTRO = "https://dadosabertos.ans.gov.br/FTP/PDA/operadoras_de_planos_de_saude_ativas/Relatorio_cadop.csv"
DEST_DIR = "./data/raw"

def download_tudo():
    if not os.path.exists(DEST_DIR):
        os.makedirs(DEST_DIR)
    
    # 1. Download dos Trimestres
    datasets = [
        {"ano": "2025", "arquivo": "1T2025.zip"},
        {"ano": "2025", "arquivo": "2T2025.zip"},
        {"ano": "2025", "arquivo": "3T2025.zip"} 
    ]

    for item in datasets:
        print(f"Baixando {item['arquivo']}...")
        try:
            r = requests.get(f"{BASE_URL}{item['ano']}/{item['arquivo']}", timeout=30)
            r.raise_for_status()
            with zipfile.ZipFile(BytesIO(r.content)) as z:
                pasta = os.path.join(DEST_DIR, item['arquivo'].replace('.zip', ''))
                z.extractall(pasta)
        except Exception as e:
            print(f"Erro ao baixar {item['arquivo']}: {e}")

    print(f"Sucesso! Arquivos baixados e extraídos com sucesso!!")

if __name__ == "__main__":
    download_tudo()