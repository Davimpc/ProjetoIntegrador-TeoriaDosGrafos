
# Projeto: Análise e Visualização Dinâmica de Grafos de Artigos Científicos do PubMed

Este projeto implementa um sistema capaz de coletar artigos científicos diretamente do PubMed, extrair suas palavras-chave oficiais (MeSH Terms), construir um grafo dinâmico e incremental e gerar visualizações interativas destacando relações entre termos médicos e publicações.

O objetivo do trabalho é aplicar conceitos de Teoria dos Grafos para explorar grandes volumes de informação biomédica de forma gráfica, escalável e navegável.

## Principais Funcionalidades
### 1. Busca Inteligente no PubMed

O usuário digita um termo (ex: avc, zika virus, dengue).

Se o termo não existir no grafo local, o sistema:

Consulta a API do PubMed (ESearch + EFetch)

Baixa novos artigos

Extrai títulos, autores e keywords (MeSH Terms)

Adiciona os novos dados ao CSV (artigos_pubmed_api.csv)

### 2. Construção Automática do Grafo

Cada artigo vira um nó.

Cada keyword MeSH vira outro nó.

O grafo é bipartido (Artigo ↔ Keyword).

O tamanho dos nós é definido pela centralidade de grau, destacando os mais importantes.

### 3. Incremento Dinâmico

Novos artigos coletados são adicionados ao grafo existente.

O sistema evita duplicações.

Corrige casos de tradução (ex: usuário busca "avc", PubMed retorna "stroke").

Padroniza tudo para minúsculas para evitar duplicações invisíveis.

### 4. Visualização Interativa (PyVis)

Duas visualizações são suportadas:

#### Visão Geral (Macro)

Mostra apenas as Top-N keywords mais centrais.

Evita "bolas de pelos" de milhares de nós.

Ideal para ver temas principais emergindo do dataset.

#### Visão Focada (Micro)

Mostra o "bairro" do termo buscado (ego graph).

Exibe apenas o termo + artigos diretamente relacionados.

Fácil de entender e explorar.

## As visualizações são geradas como arquivos HTML, abrindo diretamente no navegador:

rede_pubmed_otimizada.html

rede_pubmed_geral.html

## Instalação
#### 1. Clonar o repositório
git clone https://github.com/seu-usuario/seu-repositorio.git

cd seu-repositorio

#### 2. Instalar dependências
pip install -r requirements.txt

## Como Executar

O arquivo principal é:

buscar_no_grafo.py


### Execute:

python buscar_no_grafo.py

### Comandos disponíveis:
```markdown
Comando	   |  Função
---------------------
[termo]    |  Busca palavras-chave no grafo ou consulta PubMed
visualizar |  Mostra o grafo focado no último termo buscado
geral      |  Mostra a visão geral com as keywords mais importantes
sair       |  Fecha o programa
