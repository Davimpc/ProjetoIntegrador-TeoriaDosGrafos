import requests
import xml.etree.ElementTree as ET
import pandas as pd
import time
import os

# --- FUNÇÃO 1: BUSCAR IDs (ESearch) ---
def search_pubmed(query, max_results=50):
    """
    Busca no PubMed e retorna uma lista de IDs de artigos (PMIDs).
    """
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        'db': 'pubmed',
        'term': query,
        'retmax': max_results,
        'retmode': 'json'
    }
    
    print(f"Buscando {max_results} artigos para o termo: '{query}'...")
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status() # Verifica se a requisição foi bem sucedida
        
        data = response.json()
        id_list = data['esearchresult']['idlist']
        
        print(f"Encontrados {len(id_list)} IDs na busca.")
        return id_list
        
    except requests.exceptions.RequestException as e:
        print(f"Erro na busca (ESearch): {e}")
        return []

# --- FUNÇÃO 2: BUSCAR DETALHES (EFetch) ---
def fetch_article_details(id_list):
    """
    Busca os detalhes completos de uma lista de artigos (PMIDs).
    """
    if not id_list:
        return []

    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {
        'db': 'pubmed',
        'rettype': 'xml',
        'retmode': 'text',
        'id': ",".join(id_list)
    }
    
    print(f"Buscando detalhes de {len(id_list)} artigos...")
    
    try:
        response = requests.post(base_url, data=params) # Usando POST
        response.raise_for_status()
        
        xml_data = response.text
        root = ET.fromstring(xml_data)
        
        articles_data = []
        for article_node in root.findall('.//PubmedArticle'):
            pmid = article_node.find('.//PMID').text
            title_node = article_node.find('.//ArticleTitle')
            title = title_node.text if title_node is not None else "N/A"
            
            authors_list = []
            author_nodes = article_node.findall('.//Author')
            for author_node in author_nodes:
                lastname = author_node.find('LastName')
                forename = author_node.find('ForeName')
                if lastname is not None and forename is not None:
                    authors_list.append(f"{forename.text} {lastname.text}")
            authors_str = ", ".join(authors_list)

            # Converte keywords para minúsculas ANTES de salvar no CSV
            keywords_list = [kw.text.lower() for kw in article_node.findall('.//MeshHeading/DescriptorName')]
            
            keywords_str = ", ".join(keywords_list)

            articles_data.append({
                'pmid': pmid,
                'title': title,
                'authors': authors_str,
                'keywords': keywords_str
            })
            
        print(f"Detalhes de {len(articles_data)} artigos processados com sucesso.")
        return articles_data

    except requests.exceptions.RequestException as e:
        print(f"Erro na busca dos detalhes (EFetch): {e}")
        return []
    except ET.ParseError as e:
        print(f"Erro ao processar XML: {e}")
        return []

# --- FUNÇÃO 3: LÓGICA PRINCIPAL (A QUE ESTAVA FALTANDO) ---
def coletar_novos_artigos(search_query, max_articles=100):
    """
    Função principal que o 'buscar_no_grafo.py' chama.
    Orquestra a busca, filtragem e salvamento.
    Retorna a lista de novos artigos encontrados.
    """
    OUTPUT_FILENAME = 'artigos_pubmed_api.csv'
    existing_pmids = set()

    # --- LÓGICA ANTI-DUPLICAÇÃO ---
    try:
        if os.path.exists(OUTPUT_FILENAME):
            df_existente = pd.read_csv(OUTPUT_FILENAME)
            existing_pmids.update(df_existente['pmid'].astype(str))
            print(f"Lidos {len(existing_pmids)} PMIDs existentes do CSV.")
    except Exception as e:
        print(f"Não foi possível ler o arquivo CSV existente: {e}")

    # --- ETAPA 1: BUSCAR IDs (ESearch) ---
    found_pmids = search_pubmed(search_query, max_articles)
    
    new_pmids_to_fetch = [pmid for pmid in found_pmids if pmid not in existing_pmids]

    if not new_pmids_to_fetch:
        print("\nNenhum artigo novo encontrado para esta busca.")
        return [] # Retorna uma lista vazia
    else:
        print(f"\nEncontrados {len(new_pmids_to_fetch)} artigos novos para adicionar.")
        time.sleep(1) 
        
        # --- ETAPA 2: BUSCAR DETALHES DOS NOVOS ARTIGOS (EFetch) ---
        new_articles = fetch_article_details(new_pmids_to_fetch)
        
        if new_articles:
            # --- ETAPA 3: SALVAR/INCREMENTAR O CSV ---
            df_new = pd.DataFrame(new_articles)
            file_exists = os.path.exists(OUTPUT_FILENAME)
            
            df_new.to_csv(
                OUTPUT_FILENAME, 
                mode='a', 
                index=False, 
                header=not file_exists,
                encoding='utf-8-sig'
            )
            
            print(f"Sucesso! {len(df_new)} novos artigos foram adicionados a '{OUTPUT_FILENAME}'")
            return new_articles # Retorna os novos artigos para o 'buscar_no_grafo'
    
    return [] # Retorna lista vazia se algo falhar

# --- BLOCO DE TESTE ---
# Isso só roda se você executar 'python collector_pubmed.py' diretamente
if __name__ == "__main__":
    print("--- Testando o coletor (execução direta) ---")
    coletar_novos_artigos("zika virus", 50)