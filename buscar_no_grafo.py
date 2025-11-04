import pandas as pd
import networkx as nx

# --- CONFIGURAÇÃO ---
CAMINHO_CSV = "artigos_pubmed_api.csv"

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

print(f"Grafo carregado: {len(G.nodes)} nós e {len(G.edges)} arestas.")

# --- 3. Função de busca (ignora maiúsculas/minúsculas) ---
def buscar_conexoes(grafo, tema):
    """Busca todos os nós conectados a um tema usando BFS (sem diferença de maiúsculas/minúsculas)"""
    tema = tema.lower()

    # Procurar nós cujo nome contenha o termo (case insensitive)
    nos_correspondentes = [n for n in grafo.nodes if tema in n.lower()]

    if not nos_correspondentes:
        print(f"\n❌ Tema '{tema}' não encontrado no grafo.")
        return []

    visitados = set()
    fila = nos_correspondentes.copy()

    while fila:
        atual = fila.pop(0)
        if atual not in visitados:
            visitados.add(atual)
            fila.extend(v for v in grafo.neighbors(atual) if v not in visitados)

    return visitados

# --- 4. Executar busca ---
while True:
    tema = input("\nDigite um tema (ou 'sair' para encerrar): ").strip()
    if tema.lower() == "sair":
        print("Encerrando busca...")
        break

    resultados = buscar_conexoes(G, tema)

    if resultados:
        print(f"\n🔎 Nós conectados ao tema '{tema}':")
        for r in resultados:
            print(" -", r)
        print(f"\nTotal de {len(resultados)} nós conectados.\n")
    else:
        print("Nenhuma conexão encontrada.\n")
