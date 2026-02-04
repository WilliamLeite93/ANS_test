import os
import pandas as pd
import zipfile

CONSOLIDADO_CSV = "./data/processed/consolidado_despesas.csv"
CADASTRO_LOCAL = "./data/raw/Relatorio_cadop.csv"
SAIDA_ENRIQUECIDO = "./data/processed/consolidado_enriquecido.csv"
SAIDA_AGREGADO = "./data/processed/despesas_agregadas.csv"
NOME_ZIP = "Teste_William.zip"

def carregar_seguro(caminho, sep=';'):
    if not os.path.exists(caminho): return None
    try:
        return pd.read_csv(caminho, sep=sep, encoding='utf-8-sig', low_memory=False)
    except:
        return pd.read_csv(caminho, sep=sep, encoding='latin1', low_memory=False)

def executar_secao_2_final():
    print("--- Transformador de Dados ---")
    df_cons = carregar_seguro(CONSOLIDADO_CSV)
    df_cad = carregar_seguro(CADASTRO_LOCAL)
    
    if df_cons is None or df_cad is None:
        print("Erro: Arquivos base não encontrados.")
        return

    cols_cad = ['REGISTRO_OPERADORA', 'CNPJ', 'Razao_Social', 'Modalidade', 'UF']
    df_cad = df_cad[cols_cad].copy()
    df_cad.columns = ['reg', 'cnpj', 'raz', 'mod', 'uf']
    
    df_cons['reg'] = df_cons['reg'].astype(str).str.strip()
    df_cad['reg'] = df_cad['reg'].astype(str).str.strip()
    df_final = pd.merge(df_cons, df_cad, on='reg', how='left')
    df_final.to_csv(SAIDA_ENRIQUECIDO, index=False, sep=';', encoding='utf-8-sig')
    print("Enriquecimento concluído.")

    df_agregado = df_final.groupby(['raz', 'uf']).agg(
        valor_total=('val', 'sum'),
        media_trimestral=('val', 'mean'),
        desvio_padrao=('val', 'std')
    ).reset_index().fillna(0).sort_values(by='valor_total', ascending=False)
    
    df_agregado.to_csv(SAIDA_AGREGADO, index=False, sep=';', encoding='utf-8-sig')
    print("Agregação concluída.")

    with zipfile.ZipFile(NOME_ZIP, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(SAIDA_AGREGADO, arcname='despesas_agregadas.csv')
    print(f"Sucesso: {NOME_ZIP} gerado.")

if __name__ == "__main__":
    executar_secao_2_final()