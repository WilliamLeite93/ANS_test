import pandas as pd
from sqlalchemy import create_engine
import os

# Configurações do Banco
DB_URL = "postgresql://william_user:ans_password@localhost:5432/ans_financeiro"
ARQUIVO_BANCO = "./data/processed/consolidado_enriquecido.csv"

def carregar_para_postgres():
    if not os.path.exists(ARQUIVO_BANCO):
        print(f"Erro: Arquivo {ARQUIVO_BANCO} não encontrado.")
        return

    try:
        engine = create_engine(DB_URL)
        print("Lendo dados de /data/processed...")
        df = pd.read_csv(ARQUIVO_BANCO, sep=';')
        
        print(f"Carregando {len(df)} linhas na tabela 'despesas'...")
        df.to_sql('despesas', engine, if_exists='replace', index=False)
        print("✅ Dados carregados com sucesso!")
        
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    carregar_para_postgres()