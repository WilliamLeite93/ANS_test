import os
import requests
import zipfile
import pandas as pd
from io import BytesIO

BASE_URL = "https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/"
DEST_DIR = "./data/raw"




def download_and_extract_zip():
    if not os.path.exists(DEST_DIR):
        os.makedirs(DEST_DIR)
    
    datasets = [
        {"ano": "2025", "arquivo": "1T2025.zip"},
        {"ano": "2025", "arquivo": "2T2025.zip"},
        {"ano": "2025", "arquivo": "3T2025.zip"} 
    ]

    for item in datasets:
        ano = item["ano"]
        arquivo = item["arquivo"]

        url_completa = f"{BASE_URL}{ano}/{arquivo}"

        print(f"Baixando {url_completa}...")

        try:
            response = requests.get(url_completa, timeout=30)
            response.raise_for_status()

            with zipfile.ZipFile(BytesIO(response.content)) as zip_ref:
              pasta_destino = os.path.join(DEST_DIR, arquivo.replace('.zip', ''))
              zip_ref.extractall(pasta_destino)
              print(f"Sucesso: Extraído em {pasta_destino}")
                
        except Exception as e:
            print(f"Erro ao baixar {arquivo}: {e}")

if __name__ == "__main__":
    download_and_extract_zip()  

