from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from typing import Optional

app = FastAPI(title="ANS Financeiro API")

# Habilitar CORS para o Vue.js conseguir acessar a API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_URL = "postgresql://william_final:senha_ans_2026@localhost:5433/ans_financeiro"
engine = create_engine(DB_URL)

@app.get("/api/operadoras")
def listar_operadoras(page: int = 1, limit: int = 10, busca: Optional[str] = None):
    offset = (page - 1) * limit
    params = {"limit": limit, "offset": offset}
    
    # Base da query
    base_sql = "SELECT DISTINCT cnpj, raz, mod, uf FROM despesas"
    where_sql = ""
    
    if busca:
        where_sql = " WHERE raz ILIKE :busca OR cnpj LIKE :busca"
        params["busca"] = f"%{busca}%"
    
    with engine.connect() as conn:
        # Busca dados paginados
        data = conn.execute(text(f"{base_sql}{where_sql} LIMIT :limit OFFSET :offset"), params)
        rows = [dict(row._mapping) for row in data]
        
        # Conta total para paginação no frontend [cite: 166]
        total = conn.execute(text(f"SELECT COUNT(DISTINCT cnpj) FROM despesas{where_sql}"), params).scalar()
        
    return {"data": rows, "total": total, "page": page, "limit": limit}

from fastapi import FastAPI, HTTPException
import logging

# Configuração de log para ver o erro real no console do Uvicorn
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ... (restante do código anterior)

@app.get("/api/operadoras/{cnpj}/despesas")
def historico_despesas(cnpj: str):
    try:
        # Ajustamos para lidar com o .0 que o Pandas inseriu no seu banco
        query = """
            SELECT ano, tri, SUM(val) as valor 
            FROM despesas 
            WHERE (cnpj = :cnpj OR cnpj LIKE :cnpj_alt) AND val > 0
            GROUP BY ano, tri 
            ORDER BY ano, tri
        """
        # Limpamos o CNPJ caso ele venha com espaços ou caracteres estranhos
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
    """
    Retorna estatísticas agregadas (top 5 operadoras e UF) [cite: 145]
    """
    # Opção C: Pré-calcular ou Query direta otimizada 
    query_top_5 = """
        SELECT raz, SUM(val) as total 
        FROM despesas 
        WHERE val > 0 
        GROUP BY raz 
        ORDER BY total DESC LIMIT 5
    """
    query_uf = "SELECT uf, SUM(val) as total FROM despesas GROUP BY uf ORDER BY total DESC"
    
    with engine.connect() as conn:
        top_5 = [dict(row._mapping) for row in conn.execute(text(query_top_5))]
        dist_uf = [dict(row._mapping) for row in conn.execute(text(query_uf))]
        
    return {
        "top_5_operadoras": top_5,
        "distribuicao_uf": dist_uf
    }