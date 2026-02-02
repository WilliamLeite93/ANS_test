Teste de Engenharia de Dados - ANS
Este repositório contém a solução completa para o desafio técnico da ANS, abrangendo desde a extração e consolidação de dados financeiros até a disponibilização de uma API de alto desempenho para consulta de operadoras de saúde.

🛠️ Estrutura do Projeto
O projeto segue uma arquitetura modular para facilitar a manutenção e o isolamento de responsabilidades:

scripts/processador.py: Consolida os arquivos brutos da ANS (Trimestres), realiza a filtragem (Conta 411) e gera o arquivo consolidado inicial (Seção 2.1).

scripts/transformador.py: Executa o enriquecimento (Join com CADOP), gera as agregações estatísticas e cria o arquivo compactado para entrega (Seção 2.2 e 2.3).

scripts/carregar_banco.py: Cria a estrutura de tabelas e índices no PostgreSQL e realiza a carga dos dados processados (Seção 3).

main.py: Servidor Backend utilizando FastAPI para disponibilizar os endpoints de consulta e estatísticas (Seção 4).

/data/: Diretório organizado em raw (dados brutos) e processed (dados transformados).

🚀 Como Executar o Projeto
1. Pré-requisitos
Python 3.10+

PostgreSQL (com uma base de dados criada chamada ans_financeiro).

Node.js (Necessário para a futura etapa de Frontend).

2. Instalação e Ambiente
Crie um ambiente virtual e instale as dependências necessárias para garantir o isolamento do projeto:

PowerShell

python -m venv .venv
.venv\Scripts\activate  # No Windows
pip install -r requirements.txt
3. Pipeline de Processamento (Passo a Passo)
Os scripts devem ser executados na ordem lógica do fluxo de dados:

Consolidação: Processa os CSVs brutos dos trimestres na pasta data/raw.

python scripts/processador.py

Transformação: Cruza os dados financeiros com o cadastro de operadoras e gera as métricas.

python scripts/transformador.py

Carga no Banco: Migra os resultados para o PostgreSQL.

python scripts/carregar_banco.py

4. Execução da API
Para iniciar o servidor e acessar a documentação interativa automática (Swagger):

PowerShell

uvicorn main:app --reload
Acesse: http://127.0.0.1:8000/docs

🧠 Decisões Técnicas e Trade-offs
1. Processamento em Blocos (Memória vs. Velocidade)
Os arquivos da ANS são volumosos. Optei pelo processamento incremental por trimestre e filtragem precoce do grupo contábil 411. Isso reduz drasticamente o consumo de memória RAM, permitindo que o pipeline rode em máquinas com recursos limitados sem travamentos.

2. Otimização de Consultas (Estatísticas Pré-agregadas)
Em vez de calcular médias e desvios padrão em tempo real na API (o que seria custoso para o banco), a rota /api/estatisticas consome a tabela despesas_agregadas. Esta tabela é gerada durante a fase de transformação, garantindo respostas em milissegundos para o usuário final.

3. Modelagem de Dados e Integridade
Tipagem: Utilizei NUMERIC para valores monetários para garantir precisão decimal e TEXT para CNPJ para preservar zeros à esquerda.

Tratamento de Inconsistências: Identificamos sufixos residuais em CNPJs vindos do processamento via Pandas (.0) e implementamos buscas flexíveis com o operador LIKE no SQL para garantir que a pesquisa funcione independentemente da formatação.

CORS: Implementado middleware para permitir que o futuro frontend (Vue.js) acesse os recursos do backend sem bloqueios de segurança do navegador.

4. Índices Estratégicos
Foram criados índices nas colunas cnpj, uf e raz (Razão Social). Isso garante que buscas textuais e filtros por localização sejam instantâneos, mesmo com o banco contendo centenas de milhares de registros.