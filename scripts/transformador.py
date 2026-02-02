import os
import pandas as pd

CONSOLIDADO_CSV = "./data/processed/consolidado_despesas.csv"
CADASTRO_LOCAL = "./data/raw/Relatorio_cadop.csv"
SAIDA_BANCO = "./data/processed/consolidado_enriquecido.csv"

def carregar_seguro(caminho, sep=';'):
    # Tenta ler UTF-8, se falhar tenta Latin-1
    try:
        return pd.read_csv(caminho, sep=sep, encoding='utf-8-sig')
    except:
        return pd.read_csv(caminho, sep=sep, encoding='latin1')

def executar_secao_2():
    print("--- Passo 2: Transformador ---")
    df_cons = carregar_seguro(CONSOLIDADO_CSV)
    df_cad = carregar_seguro(CADASTRO_LOCAL)
    
    # Seleção de colunas do cadastro
    cols_cad = ['REGISTRO_OPERADORA', 'CNPJ', 'Razao_Social', 'Modalidade', 'UF']
    df_cad = df_cad[cols_cad].copy()
    df_cad.columns = ['RegistroANS', 'CNPJ', 'RazaoSocial', 'Modalidade', 'UF']
    
    # Conversão de chaves para string
    df_cons['RegistroANS'] = df_cons['RegistroANS'].astype(str).str.strip()
    df_cad['RegistroANS'] = df_cad['RegistroANS'].astype(str).str.strip()
    
    # Merge
    df_final = pd.merge(df_cons, df_cad, on='RegistroANS', how='left').dropna(subset=['CNPJ'])
    
    # LIMPEZA DE CARACTERES: Remove qualquer coisa que não seja UTF-8 válido nas strings
    for col in df_final.select_dtypes(include=['object']).columns:
        df_final[col] = df_final[col].astype(str).str.encode('utf-8', 'ignore').str.decode('utf-8')

    df_final.to_csv(SAIDA_BANCO, index=False, sep=';', encoding='utf-8-sig')
    print(f"✅ Arquivo para o banco gerado em: {SAIDA_BANCO}")

if __name__ == "__main__":
    executar_secao_2()