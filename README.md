Teste de Engenharia de Dados - ANS
Este repositório contém a solução para o desafio técnico da ANS, dividido em integração, consolidação e transformação de dados financeiros de operadoras de saúde.

🛠️ Estrutura do Projeto
O projeto segue uma arquitetura modular para facilitar a manutenção e o versionamento:

scripts/downloader.py: Responsável por acessar o servidor de dados abertos da ANS e baixar os arquivos ZIP das demonstrações contábeis.

scripts/processador.py: Realiza a extração, filtragem (Conta 411) e consolidação inicial da Seção 1.

scripts/transformador.py: Executa o enriquecimento (Join), validações matemáticas de CNPJ e gera as agregações estatísticas da Seção 2.

/data/: Pasta (ignorada no Git) que armazena os dados brutos (raw) e processados (processed).

🚀 Decisões Técnicas e Trade-offs
1. Processamento Incremental (Seção 1)
Escolha: Processamento em blocos por trimestre. Justificativa: Os arquivos da ANS são volumosos. Ao processar um trimestre por vez e filtrar apenas as contas analíticas (9 dígitos) do grupo 411, reduzimos drasticamente o consumo de memória RAM, garantindo que o pipeline rode em ambientes com recursos limitados sem travamentos (Out of Memory).

2. Tratamento de Fontes Instáveis (Seção 2)
Estratégia: Download manual e limpeza via módulo csv. Justificativa: Durante o desenvolvimento, o servidor da ANS apresentou instabilidades e bloqueios de acesso via script (HTTP 403/503). Optou-se pelo download manual do Relatorio_cadop.csv para garantir a continuidade. Além disso, o arquivo continha metadados administrativos no topo, o que exigiu uma lógica de limpeza linha a linha para identificar a "âncora" do cabeçalho real antes da carga no Pandas.

3. Validação de CNPJ e Integridade (Seção 2.1)
Estratégia: Implementação da lógica de dígitos verificadores (Módulo 11). Trade-off: Registros com CNPJ matematicamente inválidos foram descartados.

Prós: Garante que o resultado final contenha apenas entidades jurídicas reais, evitando lixo no banco de dados.

Contras: Pequena perda de dados financeiros caso a operadora tenha um erro de digitação no cadastro oficial.

4. Enriquecimento via Registro ANS (Seção 2.2)
Estratégia: Left Join utilizando RegistroANS como chave primária. Justificativa: Como os arquivos financeiros não trazem o CNPJ nativamente, utilizamos o RegistroANS (ID único da operadora) como ponte para buscar o CNPJ e a Razão Social no cadastro, garantindo 100% de precisão no cruzamento.

🔍 Análise Crítica de Dados
Valores Negativos: Registros com saldos nulos ou negativos foram removidos, pois despesas com sinistros devem ser obrigatoriamente valores positivos para fins de agregação.

Estatísticas: Foram calculados a Média e o Desvio Padrão. O desvio padrão é essencial para identificar operadoras com alta volatilidade de gastos entre os trimestres, o que pode indicar sazonalidade ou sinistros atípicos.

Ordenação: Os dados finais foram ordenados de forma decrescente pelo valor total, priorizando a visualização das operadoras com maior impacto financeiro.

📋 Como Executar
Ambiente: Recomenda-se o uso de um ambiente virtual (venv).

Dependências:

Bash

pip install pandas requests openpyxl
Execução:

Bash

# Baixar dados contábeis (Cadastro deve ser colocado em data/raw manualmente se o servidor falhar)
python scripts/downloader.py

# Gerar consolidado inicial
python scripts/processador.py

# Gerar agregação final, validação de CNPJ e ZIP
python scripts/transformador.py
Com este README, seu projeto está com uma documentação de nível sênior!

"Para a persistência de dados (Seção 3), utilizamos o SQLAlchemy pela facilidade de mapeamento objeto-relacional e o driver Psycopg2 para integração nativa com o PostgreSQL via Docker."

Crescimento (Query 1): "Optei por ignorar operadoras que não aparecem nos dois trimestres extremos, pois um crescimento de 0 para X ou de X para 0 geraria uma distorção estatística (divisão por zero ou -100%) que não reflete a performance real da operação.".


Normalização (Item 3.2): Como você criou tabelas separadas para o cadastro e para as despesas, justifique: "Escolhi a Opção B (Tabelas Normalizadas) para evitar redundância de dados cadastrais (Razão Social, UF) em cada linha de despesa, garantindo melhor integridade e menor uso de disco.".


Tipos de Dados: "Utilizei NUMERIC(18,2) para valores monetários para evitar erros de precisão comuns em tipos FLOAT, garantindo que cálculos financeiros de larga escala sejam exatos.".


Trade-off de Normalização: "Optei por uma estrutura desnormalizada para as queries analíticas visando performance em operações de leitura, visto que o volume de dados ultrapassa 350 mil registros".


Escolha de Tipos de Dados: "Utilizei NUMERIC para valores monetários para garantir precisão decimal absoluta, e TEXT para CNPJ para preservar zeros à esquerda e evitar problemas de precisão com inteiros longos".


Tratamento de Inconsistências: "Dados com valores negativos ou CNPJs inválidos foram tratados via script Python antes da carga, garantindo que as queries SQL trabalhem apenas com dados íntegros".

1. Validando as Rotas (O "Swagger")
Uma das grandes vantagens do FastAPI é a documentação automática. 

Com o servidor rodando, abra o seu navegador e acesse: http://127.0.0.1:8000/docs

Você verá as rotas /api/operadoras e /api/estatisticas listadas. 



Clique em "Try it out" na rota de operadoras e execute. Você deve ver o JSON com os dados reais do seu banco.

Cache vs Queries Diretas (4.2.3): "Para a rota /api/estatisticas, optei pela Opção A (Cálculo em tempo real). Justifico esta escolha pelo fato dos dados serem históricos e estáticos após a importação, e com os índices criados no banco, a performance é suficiente para o volume atual sem a complexidade extra de um Redis". 


Tratamento de Erros (4.3.4): "Implementei o HTTPException do FastAPI para retornar erros específicos (como 404 para CNPJs inexistentes), permitindo que o frontend forneça feedback claro ao usuário em vez de mensagens genéricas". 


CORS: "Adicionei o middleware de CORS para permitir que o servidor Vue.js (frontend) consuma a API mesmo rodando em portas diferentes durante o desenvolvimento"