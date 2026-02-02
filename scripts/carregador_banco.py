import pandas as pd
from sqlalchemy import create_engine, text
import os

DB_URL = "postgresql://william_final:senha_ans_2026@localhost:5433/ans_financeiro"
ARQUIVO_BANCO = "./data/processed/consolidado_enriquecido.csv"

def carregar_para_postgres():
    if not os.path.exists(ARQUIVO_BANCO):
        print("Arquivo não encontrado.")
        return

    try:
        # Engine com pool de conexão otimizado
        engine = create_engine(DB_URL, client_encoding='utf8')
        
        print("Lendo dados...")
        # Definir dtypes na leitura economiza memória
        df = pd.read_csv(ARQUIVO_BANCO, sep=';', encoding='utf-8')
        df.columns = ['reg', 'tri', 'ano', 'val', 'cnpj', 'raz', 'mod', 'uf']

        print("Higienizando strings...")
        for col in df.select_dtypes(include=['object', 'string']).columns:
            # Substitui NaNs por vazio para evitar erro no banco e limpa espaços
            df[col] = df[col].fillna('').astype(str).str.strip()

        print("Preparando banco de dados...")
        with engine.begin() as conn:
            conn.execute(text("DROP TABLE IF EXISTS despesas;"))
            # Tabela com tipos mais inteligentes
            conn.execute(text("""
                CREATE TABLE despesas (
                    reg TEXT,
                    tri INTEGER,
                    ano INTEGER,
                    val NUMERIC(18,2),
                    cnpj TEXT,
                    raz TEXT,
                    mod TEXT,
                    uf CHAR(2)
                );
            """))
            
            print(f"Enviando {len(df):,} linhas...")
            # method='multi' é o segredo da velocidade no Postgres
            df.to_sql(
                'despesas', 
                conn, 
                if_exists='append', 
                index=False, 
                chunksize=10000, 
                method='multi' 
            )
            print("Criando índices para performance...")
            # Índice para buscas por empresa (CNPJ)
            conn.execute(text("CREATE INDEX idx_cnpj ON despesas(cnpj);"))
            # Índice para filtros de tempo (Ano/Trimestre)
            conn.execute(text("CREATE INDEX idx_ano_tri ON despesas(ano, tri);"))
            # Índice para localização (UF)
            conn.execute(text("CREATE INDEX idx_uf ON despesas(uf);"))
            conn.execute(text("ANALYZE despesas;"))
        print("Dados carregados com sucesso.")
        
    except Exception as e:
        print(f"Falha crítica: {e}")

if __name__ == "__main__":
    carregar_para_postgres()