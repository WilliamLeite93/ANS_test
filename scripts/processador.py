import os
import pandas as pd
import zipfile

# Configurações
DATA_RAW = "./data/raw"
DATA_SAIDA = "./data/processed"
ARQUIVO_SAIDA = "consolidado_despesas.csv"
ARQUIVO_ZIP = "consolidado_despesas.zip"

def processar_dados():
    print("--- Executando Requisitos 1.2 e 1.3 ---")
    
    # Criar diretório de saída se não existir
    os.makedirs(DATA_SAIDA, exist_ok=True)
    
    lista_consolidada = []
    pastas = ["1T2025", "2T2025", "3T2025"]
    
    for nome_pasta in pastas:
        caminho_pasta = os.path.join(DATA_RAW, nome_pasta)
        if not os.path.exists(caminho_pasta):
            print(f"Aviso: Pasta {nome_pasta} não encontrada.")
            continue

        for nome_arquivo in os.listdir(caminho_pasta):
            if nome_arquivo.lower().endswith(('.csv', '.txt', '.xlsx')):
                caminho_completo = os.path.join(caminho_pasta, nome_arquivo)
                print(f"Processando: {nome_arquivo}...")
                
                if nome_arquivo.lower().endswith('.xlsx'):
                    df = pd.read_excel(caminho_completo)
                else:
                    df = pd.read_csv(caminho_completo, sep=';', encoding='latin1', low_memory=False)

                df.columns = df.columns.str.strip().str.upper()

                if 'CD_CONTA_CONTABIL' in df.columns:
                    df['CD_CONTA_CONTABIL'] = df['CD_CONTA_CONTABIL'].astype(str)
                    
                    df_filt = df[
                        (df['CD_CONTA_CONTABIL'].str.startswith('411')) & 
                        (df['CD_CONTA_CONTABIL'].str.len() == 9)
                    ].copy()

                    # --- CORREÇÃO DO ERRO DE TIPO (KISS) ---
                    # 1. Garante que é string, remove espaços e troca vírgula por ponto
                    df_filt['VL_SALDO_FINAL'] = (
                        df_filt['VL_SALDO_FINAL']
                        .astype(str)
                        .str.strip()
                        .str.replace(',', '.')
                    )
                    
                    # 2. Converte para numérico (erros viram NaN para não travar o script)
                    df_filt['VL_SALDO_FINAL'] = pd.to_numeric(df_filt['VL_SALDO_FINAL'], errors='coerce')
                    
                    # 3. Remove os NaNs gerados por erro de conversão e só então filtra > 0
                    df_filt = df_filt.dropna(subset=['VL_SALDO_FINAL'])
                    df_filt = df_filt[df_filt['VL_SALDO_FINAL'] > 0]

                    # Criando colunas obrigatórias
                    df_filt['CNPJ'] = ""
                    df_filt['RazaoSocial'] = ""
                    df_filt['Trimestre'] = nome_pasta[:2]
                    df_filt['Ano'] = nome_pasta[2:]
                    
                    df_resumo = df_filt[['CNPJ', 'RazaoSocial', 'Trimestre', 'Ano', 'VL_SALDO_FINAL']]
                    df_resumo.columns = ['CNPJ', 'RazaoSocial', 'Trimestre', 'Ano', 'ValorDespesas']
                    
                    lista_consolidada.append(df_resumo)

    if lista_consolidada:
        resultado_final = pd.concat(lista_consolidada, ignore_index=True)
        resultado_final.to_csv(os.path.join(DATA_SAIDA, ARQUIVO_SAIDA), index=False, sep=';', encoding='utf-8')
        
        caminho_zip = os.path.join(DATA_SAIDA, ARQUIVO_ZIP)
        with zipfile.ZipFile(caminho_zip, 'w') as z:
            z.write(os.path.join(DATA_SAIDA, ARQUIVO_SAIDA), arcname=ARQUIVO_SAIDA)
            
        print(f"Sucesso! O arquivo '{caminho_zip}' foi gerado.")
        print(f"Total de registros: {len(resultado_final)}")
    else:
        print("Nenhum dado processado.")

if __name__ == "__main__":
    processar_dados()