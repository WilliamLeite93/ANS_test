Teste de Engenharia de Dados - Seção 1
Este repositório contém a solução para a Seção 1: Integração e Consolidação de Dados da ANS. O projeto foi estruturado de forma modular para garantir escalabilidade e facilidade de manutenção.

Estrutura do Projeto

downloader.py: Responsável por acessar o servidor de dados abertos da ANS, baixar os arquivos ZIP dos últimos 3 trimestres e realizar a extração automática.

processador.py: Realiza a leitura dos arquivos extraídos, aplica filtros de regras de negócio, trata inconsistências e gera o arquivo consolidado final.

/data/raw/: Pasta local onde os arquivos brutos e extraídos são armazenados.

/data/processed/: Pasta onde o resultado final (consolidado_despesas.zip) é gerado.

 Decisões Técnicas e Trade-offs

1. Processamento Incremental vs. Memória
Escolha: Processamento Incremental. Justificativa: Os arquivos de Demonstrações Contábeis da ANS são extremamente volumosos. Carregar todos simultaneamente em memória (Dataframes) poderia causar o travamento do sistema (Out of Memory). Ao processar um trimestre por vez, garantimos que o script seja resiliente e rode em máquinas com recursos limitados.

2. Identificação de Despesas com Sinistros
Critério: Filtragem pelo prefixo contábil 411. Justificativa: Conforme o Plano de Contas Padrão da ANS, as despesas com Eventos e Sinistros são mapeadas estritamente no grupo 411. Para garantir a precisão dos valores e evitar a duplicidade de somar contas "pai" (sintéticas) e "filhas" (analíticas), o script filtra apenas as contas com 9 dígitos.

🔍 Análise Crítica e Tratamento de Inconsistências
Durante a consolidação (Requisito 1.3), o script aplica as seguintes regras para garantir a qualidade dos dados:

Valores Negativos e Zerados: Foram identificados registros com saldos nulos ou negativos. Como o objetivo é analisar despesas efetivas, estes registros foram descartados para não distorcer as métricas financeiras.

Normalização de Tipos: A coluna de valores foi convertida de string (padrão brasileiro com vírgula) para float, tratando erros de conversão de forma resiliente para evitar a interrupção do pipeline.

Inconsistência de Datas: Para evitar conflitos de formatos de data entre diferentes trimestres, o script extrai o Ano e o Trimestre diretamente do contexto da estrutura de diretórios, garantindo uma padronização uniforme no CSV final.

Colunas Obrigatórias: O arquivo final foi estruturado com as colunas CNPJ, RazaoSocial, Trimestre, Ano e ValorDespesas. As colunas de identificação (CNPJ e RazaoSocial) foram criadas como placeholders para serem populadas via enriquecimento na Seção 2.

📋 Como Executar

Instale as dependências necessárias: pip install pandas requests openpyxl

Execute o download dos dados: python downloader.py
Execute o processamento e consolidação: python processador.py