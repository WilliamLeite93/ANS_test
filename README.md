Como Executar o Projeto
1. Pré-requisitos

Python 3.10+ e PostgreSQL > 10.0.

Node.js para a interface Vue.js.

2. Preparação e Instalação
Na raiz do projeto:

PowerShell

python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
3. Execução do Fluxo de Dados
Os scripts devem ser executados na ordem abaixo para respeitar as dependências:

ETL - Seção 1: python scripts/processador.py (Consolidação trimestral e filtragem da conta 411).

ETL - Seção 2: python scripts/transformador.py (Join cadastral, validações e agregação estatística).

Banco - Seção 3: python scripts/carregar_banco.py (DML/DDL para carga no PostgreSQL).

API - Seção 4.2: uvicorn main:app --reload (Disponibiliza os endpoints na porta 8000).

Interface - Seção 4.3: ```powershell cd frontend npm install npm run dev


🧠 Trade-offs Técnicos e Justificativas
1. Integração e Processamento (Seção 1)
Estratégia de Processamento (1.2): Optei pelo processamento incremental por trimestre. Dado o volume massivo dos arquivos da ANS, carregar tudo em memória de uma vez causaria estouro de RAM. O processamento incremental garante estabilidade.



Tratamento de Inconsistências (1.3): Identificamos CNPJs com formatações variadas e valores negativos. A abordagem foi a normalização para string pura e filtragem de valores inválidos para manter a integridade dos cálculos.


2. Transformação e Validação (Seção 2)

CNPJs Inválidos (2.1): Registros com dígitos verificadores incorretos foram marcados como suspeitos, mas preservados para não omitir despesas reais, priorizando a visibilidade financeira.


Estratégia de Join (2.2): O Join com o CADOP foi realizado via Pandas (Left Join) utilizando o RegistroANS como chave. Registros sem match no cadastro foram mantidos para garantir que o total de despesas não fosse subestimado.


Ordenação (2.3): Realizada no final do processo de agregação para otimizar o tempo de CPU apenas no conjunto de dados reduzido.

3. Banco de Dados (Seção 3)

Normalização (3.2): Escolhi a Opção B (Tabelas separadas). Isso facilita atualizações cadastrais sem replicar dados financeiros redundantes, reduzindo o armazenamento.



Tipagem (3.2): NUMERIC para valores monetários para evitar erros de arredondamento de ponto flutuante.

4. API e Interface (Seção 4)

Framework (4.2.1): FastAPI pela documentação automática (Swagger) e performance superior a frameworks síncronos.


Estatísticas (4.2.3): Opção C (Tabela pré-calculada). Como os dados são históricos/trimestrais, não há necessidade de reprocessar milhões de linhas em cada requisição.



Busca Frontend (4.3.1): Busca no Servidor. Essencial para escalabilidade, enviando apenas o necessário para o navegador.



Gerenciamento de Estado (4.3.2): Props/Events simples, evitando complexidade desnecessária para as funcionalidades atuais.

📂 Entrega e Documentação

Coleção Postman (4.4): O arquivo ANS_API_Collection.json contém exemplos reais de requisição para todos os endpoints.