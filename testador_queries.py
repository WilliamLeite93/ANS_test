import pandas as pd
from sqlalchemy import create_engine, text
import os

DB_URL = os.getenv("DATABASE_URL", "postgresql://william_final:senha_ans_2026@localhost:5433/ans_financeiro")

def testar_analises():
    engine = create_engine(DB_URL)
    queries = {
    "Query 1 - Crescimento Percentual": """
        WITH consolidado_por_periodo AS (
            SELECT 
                cnpj, 
                raz, 
                ano, 
                tri, 
                SUM(val) as val_total
            FROM despesas
            WHERE val > 0  -- Ignora valores negativos conforme requisito [cite: 48, 51]
            GROUP BY cnpj, raz, ano, tri
        ),
        periodos AS (
            SELECT MIN(ano || tri) as inicio, MAX(ano || tri) as fim FROM consolidado_por_periodo
        ),
        primeiro_tri AS (
            SELECT cnpj, raz, val_total as valor_inicial
            FROM consolidado_por_periodo
            WHERE (ano || tri) = (SELECT inicio FROM periodos)
        ),
        ultimo_tri AS (
            SELECT cnpj, val_total as valor_final
            FROM consolidado_por_periodo
            WHERE (ano || tri) = (SELECT fim FROM periodos)
        )
        -- SELECT FINAL ADICIONADO ABAIXO:
        SELECT 
            p.raz, 
            p.cnpj,
            ((u.valor_final - p.valor_inicial) / NULLIF(p.valor_inicial, 0)) * 100 as crescimento_perc
        FROM primeiro_tri p
        JOIN ultimo_tri u ON p.cnpj = u.cnpj
        WHERE p.valor_inicial > 1000
        ORDER BY crescimento_perc DESC
        LIMIT 5;
    """,
    "Query 2 - Distribuição por UF": """
        SELECT 
            uf, 
            SUM(val) as despesa_total,
            AVG(val) as media_por_operadora,
            COUNT(DISTINCT cnpj) as total_operadoras
        FROM despesas
        GROUP BY uf
        ORDER BY despesa_total DESC
        LIMIT 5;
    """,
    "Query 3 - Acima da Média": """
        WITH media_geral AS (
            SELECT AVG(val) as valor_medio FROM despesas
        ),
        operadoras_acima AS (
            SELECT cnpj
            FROM despesas, media_geral
            WHERE despesas.val > media_geral.valor_medio
            GROUP BY cnpj
            HAVING COUNT(*) >= 2
        )
        SELECT COUNT(*) as total_operadoras_criticas FROM operadoras_acima;
    """
}

    print("--- INICIANDO TESTE DE QUERIES ---")
    with engine.connect() as conn:
        for nome, sql in queries.items():
            print(f"\n[Executando: {nome}]")
            df = pd.read_sql(text(sql), conn)
            if df.empty:
                print("Aviso: A query não retornou dados. Verifique se os filtros (Ano/Tri) existem no seu CSV.")
            else:
                print(df)

if __name__ == "__main__":
    testar_analises()
