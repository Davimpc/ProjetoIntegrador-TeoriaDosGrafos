import pandas as pd
import networkx as nx
from pyvis.network import Network

# --- CONFIGURAÇÃO ---
CAMINHO_CSV = "artigos_pubmed_api.csv"
LIMITE_NOS = 300

# --- 1. Ler CSV ---
df = pd.read_csv(CAMINHO_CSV)
df = df.fillna("")

# --- 2. Criar grafo ---
G = nx.Graph()

for _, linha in df.iterrows():
    artigo = linha["title"]
    keywords = [k.strip() for k in str(linha["keywords"]).split(",") if k.strip()]
    
    G.add_node(artigo, tipo="artigo")

    for kw in keywords:
        G.add_node(kw, tipo="keyword")
        G.add_edge(artigo, kw)

# --- 3. Reduz o grafo se for muito grande ---
if len(G.nodes) > LIMITE_NOS:
    print(f"Grafo muito grande ({len(G.nodes)} nós). Reduzindo para {LIMITE_NOS} nós.")
    subG = G.subgraph(list(G.nodes)[:LIMITE_NOS])
else:
    subG = G

print(f"Grafo final: {len(subG.nodes)} nós e {len(subG.edges)} arestas.")

# --- 4. Calcular importância dos nós ---
centralidade = nx.degree_centrality(subG)

# Normalizar tamanhos (para não ficarem gigantes)
def escala_tamanho(valor):
    return 10 + (valor * 1000)  # valor base 10 + proporcional ao grau

# --- 5. Visualizar ---
net = Network(height="750px", width="100%", bgcolor="#ffffff", font_color="#000000")
net.force_atlas_2based(gravity=-25, central_gravity=0.002, spring_length=100, spring_strength=0.08)

for node, dados in subG.nodes(data=True):
    tipo = dados["tipo"]
    cor = {"keyword": "#34A853", "artigo": "#FBBC05"}.get(tipo, "#AAAAAA")
    size = escala_tamanho(centralidade.get(node, 0))
    net.add_node(node, label=node, color=cor, size=size)

for origem, destino in subG.edges():
    net.add_edge(origem, destino)

# --- 6. Exportar ---
saida_html = "rede_pubmed_otimizada.html"

net.save_graph(saida_html)

print("\n✅ Arquivos gerados:")
print(f" - {saida_html} (abra no navegador)")
