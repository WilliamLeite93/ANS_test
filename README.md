# Sistema ANS Financeiro

Projeto full stack para processamento de demonstracoes contabeis da ANS, carga em PostgreSQL, API FastAPI e interface Vue.

## Execucao com Docker Compose

Pre-requisito: Docker Desktop instalado e em execucao.

Na raiz do projeto, execute:

```powershell
docker compose up --build
```

O Compose sobe quatro servicos:

- `db`: PostgreSQL na porta local `5434`.
- `etl`: baixa os arquivos trimestrais, processa, transforma e carrega os dados no banco.
- `api`: FastAPI na porta local `8000`.
- `frontend`: interface web na porta local `8080`.

Depois que o servico `frontend` estiver no ar, acesse:

```text
http://localhost:8080
```

A documentacao interativa da API fica em:

```text
http://localhost:8000/docs
```

## Observacoes para demo

A primeira execucao pode demorar porque o servico `etl` baixa arquivos publicos da ANS e carrega o PostgreSQL. As proximas execucoes reaproveitam o volume Docker do banco, mas o `etl` ainda reprocessa os dados para garantir que as tabelas estejam consistentes.

Se quiser reiniciar tudo do zero, incluindo o banco:

```powershell
docker compose down -v
docker compose up --build
```

## Fluxo de dados

1. `scripts/downloader.py`: baixa os demonstrativos trimestrais.
2. `scripts/processador.py`: consolida os dados financeiros da conta `411`.
3. `scripts/transformador.py`: cruza com o cadastro de operadoras e gera agregacoes.
4. `scripts/carregador_banco.py`: cria as tabelas e carrega os dados no PostgreSQL.

## Endpoints principais

- `GET /api/operadoras`
- `GET /api/operadoras/{cnpj}/despesas`
- `GET /api/estatisticas`

Tambem ha uma colecao Postman em `ANS_API_Collection.json`.
