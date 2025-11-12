import os
import webbrowser
from collector_pubmed import coletar_novos_artigos
from construir_grafo_otimizado import (
    construir_grafo_inicial, 
    incrementar_grafo, 
    visualizar_e_salvar_grafo
)

def buscar_artigos_locais(grafo, no_inicial):
    """
    Busca local simples para encontrar artigos (vizinhos) ligados à keyword.
    Retorna uma lista de tuplas (pmid, titulo).
    (Esta função já espera um 'no_inicial' em minúsculas)
    """
    if not grafo.has_node(no_inicial):
        return []
    
    artigos_encontrados = []
    for vizinho in grafo.neighbors(no_inicial):
        if grafo.nodes[vizinho].get('tipo') == 'artigo':
            titulo = grafo.nodes[vizinho].get('label', 'Título não disponível')
            artigos_encontrados.append((vizinho, titulo))
            
    return artigos_encontrados

def main():
    print("Carregando banco de dados local e construindo o grafo...")
    G = construir_grafo_inicial()
    print(f"Grafo construído com {G.number_of_nodes()} nós.")
    print("-" * 30)
    
    ultimo_termo_buscado = None

    while True:
        print("\n--- Sistema de Busca em Grafos ---")
        # --- MUDANÇA AQUI ---
        print("Opções: [digite um termo], [visualizar], [geral], [sair]")
        
        if ultimo_termo_buscado:
            print(f"  (use 'visualizar' para ver o bairro de '{ultimo_termo_buscado}')")
        
        # O comando 'geral' está sempre disponível
        print("  (use 'geral' para ver a visão geral do grafo)")
        # --- FIM DA MUDANÇA ---
            
        termo_input = input("Digite sua escolha: ").strip().lower()

        if termo_input == 'sair':
            print("Encerrando o programa. Até mais!")
            break
        
        # --- MUDANÇA AQUI: COMANDO 'GERAL' ---
        if termo_input == 'geral':
            print("\nGerando visualização geral do grafo (Top Keywords)...")
            try:
                # Chama a visualização forçando 'no_foco=None'
                caminho_html = visualizar_e_salvar_grafo(G, limite_nos_geral=150, no_foco=None)
                webbrowser.open(f"file://{os.path.realpath(caminho_html)}")
                print(f"Visualização aberta em '{caminho_html}'.")
            except Exception as e:
                print(f"Erro ao gerar visualização: {e}")
            continue # Volta ao início do loop


        if termo_input == 'visualizar':
            if not ultimo_termo_buscado:
                print("\nNenhum termo em foco. Use 'geral' para a visão geral ou pesquise um termo primeiro.")
                continue # Volta ao início do loop
                
            print(f"\nGerando visualização focada em '{ultimo_termo_buscado}'...")
            try:
                caminho_html = visualizar_e_salvar_grafo(G, limite_nos_geral=150, no_foco=ultimo_termo_buscado)
                webbrowser.open(f"file://{os.path.realpath(caminho_html)}")
                print(f"Visualização aberta em '{caminho_html}'.")
            except Exception as e:
                print(f"Erro ao gerar visualização: {e}")
            continue 
            
        # --- LÓGICA DE BUSCA E INCREMENTO ---
        termo_busca = termo_input 
        ultimo_termo_buscado = termo_busca 

        if not G.has_node(termo_busca):
            print(f"\nA palavra-chave '{termo_busca}' não foi encontrada no grafo local.")
            print("Buscando artigos online no PubMed...")
            
            novos_artigos = coletar_novos_artigos(termo_busca, max_articles=100)

            if not novos_artigos:
                ultimo_termo_buscado = None
                print("Nenhum artigo novo encontrado no PubMed para este termo.")
                continue 
            
            print("Atualizando o grafo com os novos dados...")
            G = incrementar_grafo(G, novos_artigos) 
            
            # --- Correção do bug "avc" (já está aqui) ---
            if not G.has_node(termo_busca):
                print(f"Adicionando o nó principal da busca '{termo_busca}' ao grafo.")
                G.add_node(termo_busca, tipo="keyword", label=termo_busca)
            for artigo in novos_artigos:
                pmid = str(artigo["pmid"])
                if G.has_node(pmid): 
                    if not G.has_edge(pmid, termo_busca):
                        G.add_edge(pmid, termo_busca)
            # --- Fim da correção ---
            print("Grafo atualizado com sucesso!")

        print(f"\nResultados da busca por '{termo_busca}':")
        resultados = buscar_artigos_locais(G, termo_busca)
        
        if resultados:
            for pmid, titulo in resultados:
                print(f"  - [Artigo] {titulo} (PMID: {pmid})")
        else:
            print("Nenhum artigo encontrado para esta keyword.")

if __name__ == "__main__":
    main()