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