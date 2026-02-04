import os
import pandas as pd

DATA_RAW = "./data/raw"
DATA_SAIDA = "./data/processed"

def processar_dados():
    print("---Processador de Dados---")
    os.makedirs(DATA_SAIDA, exist_ok=True)
    lista_consolidada = []
    pastas = ["1T2025", "2T2025", "3T2025"]
    
    for nome_pasta in pastas:
        caminho_pasta = os.path.join(DATA_RAW, nome_pasta)
        if not os.path.exists(caminho_pasta): continue
        for arq in os.listdir(caminho_pasta):
            if arq.lower().endswith('.csv'):
                df = pd.read_csv(os.path.join(caminho_pasta, arq), sep=';', encoding='latin1', on_bad_lines='skip', low_memory=False)
                df.columns = df.columns.str.strip().str.upper()
                if 'CD_CONTA_CONTABIL' in df.columns:
                    df_filt = df[df['CD_CONTA_CONTABIL'].astype(str).str.startswith('411')].copy()
                    df_filt['VL_SALDO_FINAL'] = pd.to_numeric(df_filt['VL_SALDO_FINAL'].astype(str).str.replace(',', '.'), errors='coerce')
                    df_filt['reg'] = df_filt['REG_ANS']
                    df_filt['tri'], df_filt['ano'] = nome_pasta[:2], nome_pasta[2:]
                    lista_consolidada.append(df_filt[['reg', 'tri', 'ano', 'VL_SALDO_FINAL']])

    if lista_consolidada:
        resultado = pd.concat(lista_consolidada, ignore_index=True)
        resultado.columns = ['reg', 'tri', 'ano', 'val']
        resultado.to_csv(os.path.join(DATA_SAIDA, "consolidado_despesas.csv"), index=False, sep=';', encoding='utf-8-sig')
        print("Financeiro consolidado com sucesso.")

if __name__ == "__main__":
    processar_dados()