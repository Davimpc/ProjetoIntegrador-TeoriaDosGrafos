import pandas as pd

NOME_DO_ARQUIVO = 'artigos_pubmed_api.csv'

try:
    # Carrega o seu banco de dados CSV para um DataFrame do pandas
    df = pd.read_csv(NOME_DO_ARQUIVO)
    
    # A coluna 'pmid' é o nosso identificador único
    # O pandas tem uma função para encontrar linhas duplicadas baseadas em uma coluna
    duplicatas = df.duplicated(subset=['pmid']).sum()
    
    print("--- Verificador de Duplicatas ---")
    print(f"Arquivo analisado: '{NOME_DO_ARQUIVO}'")
    print(f"Total de artigos no arquivo: {len(df)}")
    
    if duplicatas == 0:
        print("\n✅ SUCESSO: Nenhuma duplicata encontrada na coluna 'pmid'.")
    else:
        print(f"\n⚠️ ATENÇÃO: Foram encontradas {duplicatas} duplicatas na coluna 'pmid'!")
        # Para ver quais são as duplicatas:
        # df_duplicados = df[df.duplicated(subset=['pmid'], keep=False)]
        # print(df_duplicados.sort_values('pmid'))

except FileNotFoundError:
    print(f"Erro: O arquivo '{NOME_DO_ARQUIVO}' não foi encontrado.")
except Exception as e:
    print(f"Ocorreu um erro: {e}")