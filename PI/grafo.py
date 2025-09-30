import networkx as nx
from pyvis.network import Network

# Criar grafo em NetworkX
G = nx.Graph()

# Áreas médicas
areas = {
    "Pediatria": {"color": "lightblue"},
    "Cardiologia": {"color": "lightgreen"},
    "Ortopedia": {"color": "lightcoral"},
    "Oftalmologia": {"color": "yellow"},
    "Endocrinologia": {"color": "lightpink"},
    "Cirurgia Geral": {"color": "lightgray"},
    "Neurologia": {"color": "cyan"}
}

# Médicos e médicas históricas importantes
medicos = {
    # Pediatria
    "Abraham Jacobi": {"img": "imagens/jacobi.jpeg", "areas": ["Pediatria"]},
    "Charles West": {"img": "imagens/charles_west.jpg", "areas": ["Pediatria"]},
    "Helen Brooke Taussig": {"img": "imagens/taussig.jpg", "areas": ["Pediatria", "Cardiologia"]},
    "Virginia Apgar": {"img": "imagens/apgar.jpg", "areas": ["Pediatria", "Cirurgia Geral"]},

    # Cardiologia
    "Willem Einthoven": {"img": "imagens/willem.webp", "areas": ["Cardiologia"]},
    "Andreas Gruentzig": {"img": "imagens/andreas-gruntzig.webp", "areas": ["Cardiologia"]},
    "Maude Abbott": {"img": "imagens/abbott.jpg", "areas": ["Cardiologia"]},

    # Ortopedia
    "Nicolas Andry": {"img": "imagens/nicolas_andry.jpg", "areas": ["Ortopedia"]},
    "Hugh Owen Thomas": {"img": "imagens/hugh_owen_thomas.jpg", "areas": ["Ortopedia"]},
    "Jacquelin Perry": {"img": "imagens/perry.jpg", "areas": ["Ortopedia"]},

    # Oftalmologia
    "Albrecht von Graefe": {"img": "imagens/graefe.jpg", "areas": ["Oftalmologia"]},
    "Hermann von Helmholtz": {"img": "imagens/helmholtz.jpg", "areas": ["Oftalmologia", "Neurologia"]},
    "Isabel Hayes Chapin Barrows": {"img": "imagens/barrows.png", "areas": ["Oftalmologia"]},

    # Endocrinologia
    "Thomas Addison": {"img": "imagens/addison.jpg", "areas": ["Endocrinologia"]},
    "Harvey Cushing": {"img": "imagens/cushing.jpg", "areas": ["Endocrinologia", "Cirurgia Geral", "Neurologia"]},
    "Rosalyn Yalow": {"img": "imagens/yalow.jpg", "areas": ["Endocrinologia"]},
    "Gerty Cori": {"img": "imagens/cori.jpg", "areas": ["Endocrinologia", "Cirurgia Geral"]},

    # Cirurgia Geral
    "Ambroise Paré": {"img": "imagens/pare.jpg", "areas": ["Cirurgia Geral"]},
    "Joseph Lister": {"img": "imagens/lister.jpg", "areas": ["Cirurgia Geral"]},
    "Mary Edwards Walker": {"img": "imagens/walker.jpg", "areas": ["Cirurgia Geral"]},

    # Neurologia
    "Jean-Martin Charcot": {"img": "imagens/charcot.jpg", "areas": ["Neurologia"]},
    "Santiago Ramón y Cajal": {"img": "imagens/cajal.jpg", "areas": ["Neurologia"]},
    "Rita Levi-Montalcini": {"img": "imagens/montalcini.jpg", "areas": ["Neurologia", "Endocrinologia"]},
    "Augusta Dejerine-Klumpke": {"img": "imagens/klumpke.jpg", "areas": ["Neurologia"]}
}

# Criar rede no PyVis
net = Network(height="700px", width="100%", bgcolor="#ffffff", font_color="black")

# Adicionar áreas
for area, props in areas.items():
    net.add_node(area, label=area, color=props["color"], size=40, shape="ellipse")
    G.add_node(area, label=area, type="area")

# Adicionar médicos e conexões
for medico, props in medicos.items():
    net.add_node(
        medico,
        label=medico,
        shape="circularImage",
        image=props["img"],
        size=25
    )
    G.add_node(medico, label=medico, type="medico")
    
    for area in props["areas"]:
        net.add_edge(area, medico)
        G.add_edge(area, medico)

# Gerar HTML interativo
net.write_html("medicina_grafo.html")
