import pandas as pd
from sqlalchemy import create_engine, text

DB_URL = "postgresql://william_final:senha_ans_2026@localhost:5433/ans_financeiro"
ARQUIVO_CSV = "./data/processed/consolidado_enriquecido.csv"

def validar():
    engine = create_engine(DB_URL)
    
    print("--- INICIANDO VALIDAÇÃO CRUZADA ---")
    
    df_csv = pd.read_csv(ARQUIVO_CSV, sep=';')
    qtd_csv = len(df_csv)
    
    with engine.connect() as conn:
        qtd_db = conn.execute(text("SELECT COUNT(*) FROM despesas")).scalar()
    
    print(f"\n1. Quantidade de Linhas:")
    print(f"   - No CSV: {qtd_csv}")
    print(f"   - No Banco: {qtd_db}")
    if qtd_csv == qtd_db:
        print("MATCH! O número de linhas está correto.")
    else:
        print("ERRO! O número de linhas diverge.")

    df_csv['val'] = pd.to_numeric(df_csv.iloc[:, 3], errors='coerce').fillna(0)
    soma_csv = df_csv['val'].sum()
    
    with engine.connect() as conn:
        soma_db = conn.execute(text("SELECT SUM(val) FROM despesas")).scalar()
    
    print(f"\n2. Soma Total de Despesas:")
    print(f"   - No CSV: {soma_csv:,.2f}")
    print(f"   - No Banco: {soma_db:,.2f}")
    
    print(f"\n3. Investigando Unimed Cuiabá (CNPJ 3533726000188):")
    with engine.connect() as conn:
        detalhe = pd.read_sql(text("""
            SELECT ano, tri, val 
            FROM despesas 
            WHERE cnpj LIKE '3533726000188%'
            ORDER BY ano, tri
        """), conn)
        print(detalhe)

if __name__ == "__main__":
    validar()