from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="ANS Financeiro API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_URL = "postgresql://william_final:senha_ans_2026@localhost:5433/ans_financeiro"
engine = create_engine(DB_URL)

@app.get("/api/operadoras")
def listar_operadoras(page: int = 1, limit: int = 10, busca: Optional[str] = None):
    offset = (page - 1) * limit
    params = {"limit": limit, "offset": offset}
    
    base_sql = "SELECT DISTINCT cnpj, raz, mod, uf FROM despesas"
    where_sql = ""
    
    if busca:
        where_sql = " WHERE raz ILIKE :busca OR cnpj LIKE :busca"
        params["busca"] = f"%{busca}%"
    
    try:
        with engine.connect() as conn:
            data = conn.execute(text(f"{base_sql}{where_sql} LIMIT :limit OFFSET :offset"), params)
            rows = [dict(row._mapping) for row in data]
            total = conn.execute(text(f"SELECT COUNT(DISTINCT cnpj) FROM despesas{where_sql}"), params).scalar()
            
        return {"data": rows, "total": total, "page": page, "limit": limit}
    except Exception as e:
        logger.error(f"Erro na listagem: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar operadoras")

@app.get("/api/operadoras/{cnpj}/despesas")
def historico_despesas(cnpj: str):
    try:
        query = """
            SELECT ano, tri, SUM(val) as valor 
            FROM despesas 
            WHERE (cnpj = :cnpj OR cnpj LIKE :cnpj_alt) AND val > 0
            GROUP BY ano, tri 
            ORDER BY ano, tri
        """
        cnpj_clean = cnpj.strip()
        
        with engine.connect() as conn:
            result = conn.execute(text(query), {
                "cnpj": cnpj_clean, 
                "cnpj_alt": f"{cnpj_clean}%" 
            })
            historico = [dict(row._mapping) for row in result]
            
        if not historico:
            return {"mensagem": "Nenhum dado financeiro encontrado para este CNPJ", "historico": []}
            
        return {"cnpj": cnpj, "historico": historico}
    except Exception as e:
        logger.error(f"Erro ao buscar histórico: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno ao processar a consulta")

@app.get("/api/estatisticas")
def obter_estatisticas():
    query_top_5 = "SELECT raz, valor_total as total FROM despesas_agregadas ORDER BY valor_total DESC LIMIT 5"
    query_uf = "SELECT uf, SUM(valor_total) as total FROM despesas_agregadas GROUP BY uf ORDER BY total DESC"
    
    try:
        with engine.connect() as conn:
            top_5 = [dict(row._mapping) for row in conn.execute(text(query_top_5))]
            dist_uf = [dict(row._mapping) for row in conn.execute(text(query_uf))]
            
        return {
            "top_5_operadoras": top_5,
            "distribuicao_uf": dist_uf,
            "fonte": "tabela_agregada_otimizada"
        }
    except Exception as e:
        logger.error(f"Erro nas estatísticas: {e}")
        raise HTTPException(status_code=500, detail="Erro ao gerar estatísticas")