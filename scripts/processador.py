import os
import pandas as pd
import zipfile

DATA_RAW = "./data/raw"
DATA_SAIDA = "./data/processed"

def processar_dados():
    print("--- Executando Processador ---")
    os.makedirs(DATA_SAIDA, exist_ok=True)
    
    lista_consolidada = []
    pastas = ["1T2025", "2T2025", "3T2025"]
    
    for nome_pasta in pastas:
        caminho_pasta = os.path.join(DATA_RAW, nome_pasta)
        if not os.path.exists(caminho_pasta): continue

        for arq in os.listdir(caminho_pasta):
            if arq.lower().endswith('.csv'):
                print(f"Processando: {arq}")
                df = pd.read_csv(os.path.join(caminho_pasta, arq), sep=';', encoding='latin1', low_memory=False)
                df.columns = df.columns.str.strip().str.upper()

                # Filtro Conta 411 (Sinistros)
                if 'CD_CONTA_CONTABIL' in df.columns:
                    df['CD_CONTA_CONTABIL'] = df['CD_CONTA_CONTABIL'].astype(str)
                    df_filt = df[(df['CD_CONTA_CONTABIL'].str.startswith('411')) & (df['CD_CONTA_CONTABIL'].str.len() == 9)].copy()
                    
                    df_filt['VL_SALDO_FINAL'] = pd.to_numeric(df_filt['VL_SALDO_FINAL'].astype(str).str.replace(',', '.'), errors='coerce')
                    df_filt = df_filt[df_filt['VL_SALDO_FINAL'] > 0]

                    # Mapeamos o REG_ANS para RegistroANS
                    df_filt['RegistroANS'] = df_filt['REG_ANS']
                    df_filt['Trimestre'] = nome_pasta[:2]
                    df_filt['Ano'] = nome_pasta[2:]
                    
                    lista_consolidada.append(df_filt[['RegistroANS', 'Trimestre', 'Ano', 'VL_SALDO_FINAL']])

    if lista_consolidada:
        resultado = pd.concat(lista_consolidada, ignore_index=True)
        # Criamos as colunas pedidas no 1.3 (vazias, para serem preenchidas no transformador)
        resultado['CNPJ'] = ""
        resultado['RazaoSocial'] = ""
        
        resultado = resultado[['CNPJ', 'RazaoSocial', 'Trimestre', 'Ano', 'VL_SALDO_FINAL', 'RegistroANS']]
        resultado.columns = ['CNPJ', 'RazaoSocial', 'Trimestre', 'Ano', 'ValorDespesas', 'RegistroANS']
        
        resultado.to_csv(os.path.join(DATA_SAIDA, "consolidado_despesas.csv"), index=False, sep=';', encoding='utf-8')
        print("Arquivo consolidado gerado com sucesso.")

if __name__ == "__main__":
    processar_dados()