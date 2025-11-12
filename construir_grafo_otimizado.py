import pandas as pd
import networkx as nx
from pyvis.network import Network
import os

# --- CONSTANTES ---
CAMINHO_CSV = "artigos_pubmed_api.csv"
SAIDA_HTML = "rede_pubmed_otimizada.html"

# A LISTA DE STOP WORDS QUE VOCÊ SUGERIU!
# Sinta-se à vontade para adicionar mais palavras genéricas aqui
STOP_WORDS = {
    "humans", "human", "male", "female", "adult", "child", "infant", "preschool",
    "animals", "animal", "mice", "bovine", "case-control studies", "cross-sectional studies",
    "cohort studies", "prospective studies", "retrospective studies", "middle aged",
    "young adult", "adolescent", "pregnancy", "pregnancy complications", "brazil",
    "latin america", "south america", "serologic tests", "phylogeny", "viral", "aged","cell line",
    "zika virus infection"
}


def construir_grafo_inicial():
    """
    Lê o CSV, converte keywords para minúsculas, filtra stop words 
    e constrói o grafo inicial.
    """
    print("Construindo grafo inicial a partir do CSV...")
    G = nx.Graph()
    
    if not os.path.exists(CAMINHO_CSV):
        print(f"Aviso: Arquivo '{CAMINHO_CSV}' não encontrado. Iniciando com grafo vazio.")
        return G

    try:
        df = pd.read_csv(CAMINHO_CSV)
        df = df.fillna("") 

        for _, linha in df.iterrows():
            pmid = str(linha["pmid"]) 
            title = linha["title"]
            
            # Converte para minúsculas e remove stop words
            keywords_raw = str(linha["keywords"]).split(",")
            keywords = [k.strip().lower() for k in keywords_raw if k.strip()]
            
            # Adiciona nó do artigo
            if not G.has_node(pmid):
                G.add_node(pmid, tipo="artigo", label=title)

            # Adiciona nós de keyword (já filtrados)
            for kw in keywords:
                if kw and kw not in STOP_WORDS: # Verifica se não está na stop list
                    if not G.has_node(kw):
                        G.add_node(kw, tipo="keyword", label=kw)
                    if not G.has_edge(pmid, kw):
                        G.add_edge(pmid, kw)
                    
        print(f"Grafo inicial construído com {G.number_of_nodes()} nós.")
        return G
        
    except Exception as e:
        print(f"Erro ao construir grafo do CSV: {e}")
        return G


def incrementar_grafo(g_existente, lista_novos_artigos):
    """
    Adiciona novos artigos a um grafo existente.
    Também converte para minúsculas e filtra stop words.
    """
    G = g_existente 
    
    for artigo in lista_novos_artigos:
        pmid = str(artigo["pmid"])
        title = artigo["title"]
        
        # Converte para minúsculas e remove stop words
        keywords_str = str(artigo.get("keywords", ""))
        keywords_raw = keywords_str.split(",")
        keywords = [k.strip().lower() for k in keywords_raw if k.strip()]

        if not G.has_node(pmid):
            G.add_node(pmid, tipo="artigo", label=title)

        for kw in keywords:
            if kw and kw not in STOP_WORDS: # Verifica se não está na stop list
                if not G.has_node(kw):
                    G.add_node(kw, tipo="keyword", label=kw)
                if not G.has_edge(pmid, kw):
                    G.add_edge(pmid, kw)

    print(f"Grafo incrementado com {len(lista_novos_artigos)} novos artigos.")
    return G


def visualizar_e_salvar_grafo(G, limite_nos_geral=300, no_foco=None):
    """
    Pega um objeto nx.Graph e salva um HTML com a visualização corrigida.
    """
    print("Iniciando visualização e salvamento do grafo...")
    
    subG = None
    if no_foco and G.has_node(no_foco):
        print(f"Gerando visualização focada no 'bairro' do nó: {no_foco}")
        subG = nx.ego_graph(G, no_foco, radius=1)
    else:
        if no_foco:
            print(f"Aviso: Nó de foco '{no_foco}' não encontrado. Gerando visualização geral.")
        print("Gerando visualização geral das comunidades mais importantes...")
        
        keywords = {n for n, d in G.nodes(data=True) if d.get("tipo") == "keyword"}
        if not keywords:
            print("Nenhuma keyword encontrada no grafo. Mostrando grafo como está.")
            subG = G
        else:
            centralidade_keywords = nx.degree_centrality(G)
            centralidade_keywords = {k: v for k, v in centralidade_keywords.items() if k in keywords}
            limite_keywords = 50
            top_keywords = sorted(centralidade_keywords, key=centralidade_keywords.get, reverse=True)[:limite_keywords]
            nodes_para_manter = set(top_keywords)
            for kw in top_keywords:
                nodes_para_manter.update(G.neighbors(kw)) 
            
            if len(nodes_para_manter) > 500: 
                 print(f"Bairro das top {limite_keywords} keywords é muito grande. Reduzindo para top 10.")
                 top_keywords = top_keywords[:20] #
                 nodes_para_manter = set(top_keywords)
                 for kw in top_keywords:
                     nodes_para_manter.update(G.neighbors(kw))
            
            subG = G.subgraph(nodes_para_manter)
            if subG.number_of_nodes() == 0:
                print("Filtragem resultou em grafo vazio. Mostrando grafo geral (limitado).")
                nodes_para_manter = list(G.nodes)[:limite_nos_geral]
                subG = G.subgraph(nodes_para_manter)

    print(f"Grafo final para visualização: {len(subG.nodes)} nós e {len(subG.edges)} arestas.")

    centralidade = nx.degree_centrality(subG)

    # --- CORREÇÃO DE TAMANHO DO NÓ ---
    def escala_tamanho(valor):
        # --- SEU NOVO PAINEL DE CONTROLE DE TAMANHO ---
        
        # 1. Tamanho base: Este é o tamanho mínimo de um nó.
        #    Aumentei para 30 para que os nós de artigo não fiquem tão pequenos.
        tamanho_base = 30 
        
        # 2. Multiplicador: Este é o fator de "importância".
        #    Reduzi de 1000 para 200 para evitar o "nó-sol" gigante.
        multiplicador = 200

        return tamanho_base + (valor * multiplicador) 

    net = Network(height="750px", width="100%", bgcolor="#ffffff", font_color="#000000")
    
    net.force_atlas_2based(
        gravity=-50,
        central_gravity=0.01,
        spring_length=250,
        spring_strength=0.05,
        damping=0.9
    )

    # --- CORREÇÃO DE ESTILO (FONTE E POSIÇÃO) ---
    for node, dados in subG.nodes(data=True):
        tipo = dados.get("tipo", "desconhecido")
        label = dados.get("label", node)
        centralidade_valor = centralidade.get(node, 0)
        size = escala_tamanho(centralidade_valor)
        tooltip = f"Tipo: {tipo}\nCentralidade: {centralidade_valor:.4f}"

        if tipo == "keyword":
            # --- SEU PAINEL DE CONTROLE PARA KEYWORDS ---
            
            # 1. FORMA: (dot, box, circle, ellipse colocam o texto DENTRO)
            formato = "dot"  # <-- Garanta que está "dot" ou "box"
            
            # 2. TAMANHO DA FONTE:
            tamanho_fonte = 150  # <-- Aumente este número (ex: 40)

            # 3. COR DA FONTE:
            cor_fonte = "#FFFFFF" # <-- Branco, para contrastar

            # 4. OUTROS ESTILOS
            cor_preenchimento = "#34A853" # Verde
            cor_borda = "#000000"         # Borda preta
            largura_borda = 2
            
            # Monta o dicionário de fonte
            propriedades_fonte = {'size': tamanho_fonte, 'align': 'center', 'color': cor_fonte}
        
        elif tipo == "artigo":
            cor_preenchimento = "#FBBC05"
            formato = "dot"
            cor_borda = "#E1AB04"
            largura_borda = 1
            # FONTE: Tamanho 12, centralizada (para caber no círculo)
            propriedades_fonte = {'size': 8, 'align': 'center'}
        
        else:
            cor_preenchimento = "#AAAAAA"
            formato = "dot"
            cor_borda = "#999999"
            largura_borda = 1
            propriedades_fonte = {'size': 12, 'align': 'center'}

        net.add_node(
            node,
            label=label,
            color=cor_preenchimento,
            shape=formato,
            borderColor=cor_borda,
            borderWidth=largura_borda,
            borderWidthSelected=3,
            size=size,
            title=tooltip,
            font=propriedades_fonte  # Passa as propriedades da fonte
        )
    # --- FIM DA CORREÇÃO DE ESTILO ---

    for origem, destino in subG.edges():
        net.add_edge(origem, destino)

    net.save_graph(SAIDA_HTML)
    print(f"\n✅ Visualização salva em: {SAIDA_HTML} (abra no navegador)")
    return SAIDA_HTML


if __name__ == "__main__":
    print("--- Testando a construção do grafo ---")
    grafo_teste = construir_grafo_inicial()
    
    if grafo_teste.number_of_nodes() > 0:
        print(f"Grafo teste inicial criado com {grafo_teste.number_of_nodes()} nós.")
        
        print("\n--- Testando o incremento do grafo ---")
        artigo_falso = [{
            'pmid': '000001',
            'title': 'Artigo de Teste Falso Sobre Grafos',
            'authors': 'Autor Teste',
            'keywords': 'Teste, Python, Grafos' # O incremento vai converter para minúsculas
        }]
        
        grafo_teste = incrementar_grafo(grafo_teste, artigo_falso)
        print(f"Após incremento, grafo tem {grafo_teste.number_of_nodes()} nós.")
        print(f"Nó 'teste' (minúsculo) existe? {grafo_teste.has_node('teste')}")
        
        print("\n--- Testando a visualização ---")
        visualizar_e_salvar_grafo(grafo_teste, limite_nos_geral=500, no_foco='teste')
    else:
        print("CSV vazio ou não encontrado. Teste pulado.")