import pandas as pd
from sqlalchemy import create_engine, text
import os

DB_URL = os.getenv("DATABASE_URL", "postgresql://william_final:senha_ans_2026@localhost:5433/ans_financeiro")
ARQUIVO_ENRIQUECIDO = "./data/processed/consolidado_enriquecido.csv"
ARQUIVO_AGREGADO = "./data/processed/despesas_agregadas.csv"

def carregar_para_postgres():
    if not os.path.exists(ARQUIVO_ENRIQUECIDO) or not os.path.exists(ARQUIVO_AGREGADO):
        print("Arquivos necessários não encontrados em ./data/processed/")
        return

    try:
        engine = create_engine(DB_URL, client_encoding='utf8')
        
        print("Lendo dados enriquecidos...")
        df = pd.read_csv(ARQUIVO_ENRIQUECIDO, sep=';', encoding='utf-8')
        df.columns = ['reg', 'tri', 'ano', 'val', 'cnpj', 'raz', 'mod', 'uf']

        print("Higienizando strings...")
        for col in df.select_dtypes(include=['object', 'string']).columns:
            df[col] = df[col].fillna('').astype(str).str.strip()

        print("Preparando tabelas no banco...")
        with engine.begin() as conn:
            conn.execute(text("DROP TABLE IF EXISTS despesas CASCADE;"))
            conn.execute(text("""
                CREATE TABLE despesas (
                    reg TEXT,
                    tri TEXT, -- Alterado para TEXT pois os dados são '1T', '2T', etc.
                    ano INTEGER,
                    val NUMERIC(18,2),
                    cnpj TEXT,
                    raz TEXT,
                    mod TEXT,
                    uf CHAR(2)
                );
            """))
            
            print(f"Enviando {len(df):,} linhas para 'despesas'...")
            df.to_sql('despesas', conn, if_exists='append', index=False, chunksize=10000, method='multi')

            print("Lendo dados agregados...")
            df_ag = pd.read_csv(ARQUIVO_AGREGADO, sep=';', encoding='utf-8')
            
            conn.execute(text("DROP TABLE IF EXISTS despesas_agregadas;"))
            conn.execute(text("""
                CREATE TABLE despesas_agregadas (
                    raz TEXT,
                    uf CHAR(2),
                    valor_total NUMERIC(18,2),
                    media_trimestral NUMERIC(18,2),
                    desvio_padrao NUMERIC(18,2)
                );
            """))

            print(f"Enviando {len(df_ag):,} linhas para 'despesas_agregadas'...")
            df_ag.to_sql('despesas_agregadas', conn, if_exists='append', index=False, method='multi')

            print("Criando índices...")
            conn.execute(text("CREATE INDEX idx_cnpj ON despesas(cnpj);"))
            conn.execute(text("CREATE INDEX idx_uf ON despesas(uf);"))
            conn.execute(text("CREATE INDEX idx_agregado_raz ON despesas_agregadas(raz);"))
            
            conn.execute(text("ANALYZE despesas;"))
            conn.execute(text("ANALYZE despesas_agregadas;"))

        print("Todas as tabelas foram carregadas e otimizadas com sucesso!")
            
    except Exception as e:
        print(f"Falha crítica: {e}")

if __name__ == "__main__":
    carregar_para_postgres()
