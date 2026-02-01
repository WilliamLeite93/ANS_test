import os
import pandas as pd
import re
import zipfile
import csv

# Configuração de Caminhos
DATA_RAW = "./data/raw"
DATA_PROCESSED = "./data/processed"
CONSOLIDADO_CSV = os.path.join(DATA_PROCESSED, "consolidado_despesas.csv")
CADASTRO_LOCAL = os.path.join(DATA_RAW, "Relatorio_cadop.csv")

# Saídas
SAIDA_AGREGADA = os.path.join(DATA_PROCESSED, "despesas_agregadas.csv")
SAIDA_BANCO = os.path.join(DATA_PROCESSED, "consolidado_enriquecido.csv")
SAIDA_ZIP = os.path.join(DATA_PROCESSED, "Teste_William.zip")

def validar_cnpj(cnpj):
    cnpj = re.sub(r'\D', '', str(cnpj))
    if len(cnpj) != 14 or cnpj in [s * 14 for s in "0123456789"]:
        return False
    def calc_digito(digits, weights):
        s = sum(int(d) * w for d, w in zip(digits, weights))
        r = s % 11
        return 0 if r < 2 else 11 - r
    d1 = calc_digito(cnpj[:12], [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    d2 = calc_digito(cnpj[:12] + str(d1), [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    return cnpj[-2:] == f"{d1}{d2}"

def executar_secao_2():
    print("--- Iniciando Transformação (Saídas em /data) ---")
    os.makedirs(DATA_PROCESSED, exist_ok=True)
    
    # 1. Carregar Consolidado
    df_cons = pd.read_csv(CONSOLIDADO_CSV, sep=';')
    df_cons['RegistroANS'] = df_cons['RegistroANS'].astype(str).str.strip()

    # 2. Carregar Cadastro Manual
    dados = []
    cabecalho_real = None
    with open(CADASTRO_LOCAL, 'r', encoding='latin1') as f:
        leitor = csv.reader(f, delimiter=';')
        for linha in leitor:
            if not linha: continue
            if 'REGISTRO_OPERADORA' in linha:
                cabecalho_real = [c.strip() for c in linha]
                continue
            if cabecalho_real and len(linha) == len(cabecalho_real):
                dados.append(linha)

    df_cad = pd.DataFrame(dados, columns=cabecalho_real)
    df_cad = df_cad.rename(columns={'REGISTRO_OPERADORA': 'RegistroANS', 'Razao_Social': 'RazaoSocial'})
    df_cad['RegistroANS'] = df_cad['RegistroANS'].astype(str).str.strip()

    # 3. Join
    print("Enriquecendo dados...")
    df_cons = df_cons.drop(columns=['CNPJ', 'RazaoSocial'], errors='ignore')
    df_final = pd.merge(df_cons, df_cad[['RegistroANS', 'CNPJ', 'RazaoSocial', 'Modalidade', 'UF']], on='RegistroANS', how='left')

    # 4. Validações e Limpeza
    print("Limpando e validando dados...")
    df_final = df_final.dropna(subset=['CNPJ', 'RazaoSocial'])
    df_final['ValorDespesas'] = pd.to_numeric(df_final['ValorDespesas'], errors='coerce')
    df_final['CNPJ_VALIDO'] = df_final['CNPJ'].apply(validar_cnpj)
    
    df_clean = df_final[(df_final['CNPJ_VALIDO'] == True) & (df_final['ValorDespesas'] > 0)].copy()

    # --- Salva dado detalhado para o Banco (Seção 3) ---
    df_clean.to_csv(SAIDA_BANCO, index=False, sep=';', encoding='utf-8')

    # 5. Agregação para o ZIP (Seção 2.3)
    print("Gerando agregação...")
    df_agregado = df_clean.groupby(['RazaoSocial', 'UF']).agg(
        Total_Despesas=('ValorDespesas', 'sum'),
        Media_Trimestral=('ValorDespesas', 'mean'),
        Desvio_Padrao=('ValorDespesas', 'std')
    ).reset_index().fillna(0).sort_values(by='Total_Despesas', ascending=False)

    # 6. Salvamento Final na pasta data/processed
    df_agregado.to_csv(SAIDA_AGREGADA, index=False, sep=';', encoding='utf-8')
    
    with zipfile.ZipFile(SAIDA_ZIP, 'w') as z:
        z.write(SAIDA_AGREGADA, os.path.basename(SAIDA_AGREGADA))
    
    print(f"Sucesso! Arquivos salvos em {DATA_PROCESSED}")

if __name__ == "__main__":
    executar_secao_2()