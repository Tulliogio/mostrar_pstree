import json
import networkx as nx
import matplotlib.pyplot as plt
from collections import deque, defaultdict

# Cargar datos
with open("pstree.json") as f:
    data = json.load(f)

G = nx.DiGraph()

# SOLO los procesos MÁS importantes que queremos ver
VERY_IMPORTANT_PROCESSES = {
    'explorer.exe', 'chrome.exe', 'firefox.exe', 'notepad.exe', 
    'cmd.exe', 'powershell.exe', 'python.exe', 'code.exe',
    'discord.exe', 'teams.exe', 'steam.exe', 'winrar.exe'
}

# Procesos raíz que SIEMPRE incluimos para estructura básica
ROOT_PROCESSES = {'system', 'services.exe', 'wininit.exe', 'smss.exe'}

def is_very_important(name):
    """Solo los procesos MUY importantes"""
    if not name:
        return False
    name_lower = name.lower()
    return name_lower in VERY_IMPORTANT_PROCESSES

def is_root_process(name):
    """Procesos raíz necesarios para la estructura"""
    if not name:
        return False
    return name.lower() in ROOT_PROCESSES

def should_include_process(name, parent_name=None):
    """Decide si incluir un proceso en el grafo"""
    if not name:
        return False
    
    # Incluir procesos muy importantes
    if is_very_important(name):
        return True
    
    # Incluir procesos raíz para estructura
    if is_root_process(name):
        return True
    
    # NO incluir nada más
    return False

# Función simplificada que solo agrega procesos importantes
def add_important_nodes(node, parent_name=None, depth=0):
    pid = node.get("PID")
    name = node.get("ImageFileName") or f"PID {pid}"
    
    # Limitar profundidad drásticamente
    if depth > 3:
        return
    
    # Solo agregar si es importante
    if should_include_process(name, parent_name):
        G.add_node(pid, label=name, depth=depth)
    
    # Procesar hijos
    for child in node.get("__children", []):
        child_pid = child.get("PID")
        child_name = child.get("ImageFileName") or f"PID {child_pid}"
        
        # Si el hijo es importante, agregarlo y conectarlo
        if should_include_process(child_name, name):
            G.add_node(child_pid, label=child_name, depth=depth + 1)
            
            # Solo conectar si el padre también está en el grafo
            if pid in G.nodes():
                G.add_edge(pid, child_pid)
        
        # Continuar recursión
        add_important_nodes(child, name, depth + 1)

# Procesar todos los nodos
for root_node in data:
    add_important_nodes(root_node)

# Si no hay nodos, mostrar solo System y algunos hijos importantes
if len(G.nodes()) == 0:
    print("No se encontraron procesos importantes específicos")
    print("Mostrando estructura básica del sistema...")
    
    # Agregar manualmente algunos procesos básicos
    for root_node in data:
        pid = root_node.get("PID")
        name = root_node.get("ImageFileName")
        if name == "System":
            G.add_node(pid, label=name, depth=0)
            
            # Agregar solo algunos hijos interesantes
            for child in root_node.get("__children", [])[:3]:  # Solo primeros 3
                child_pid = child.get("PID")
                child_name = child.get("ImageFileName")
                G.add_node(child_pid, label=child_name, depth=1)
                G.add_edge(pid, child_pid)

# Encontrar raíces
all_nodes = set(G.nodes())
child_nodes = set(e[1] for e in G.edges())
roots = list(all_nodes - child_nodes)

if not roots and len(G.nodes()) > 0:
    # Si no hay raíces claras, tomar el nodo con menor PID
    roots = [min(G.nodes())]

print(f"Total de nodos importantes: {len(G.nodes())}")
print(f"Raíces: {len(roots)}")

# Posicionamiento simple y limpio
def simple_layout(G, roots):
    pos = {}
    
    if len(G.nodes()) <= 10:
        levels = {}
        visited = set()
        queue = deque()
        
        # Asignar niveles
        for root in roots:
            queue.append((root, 0))
            visited.add(root)
            levels[root] = 0
        
        while queue:
            node, level = queue.popleft()
            for child in G.successors(node):
                if child not in visited:
                    visited.add(child)
                    levels[child] = level + 1
                    queue.append((child, level + 1))
        
        # Posicionar por niveles
        level_nodes = defaultdict(list)
        for node, level in levels.items():
            level_nodes[level].append(node)
        
        for level, nodes in level_nodes.items():
            y = -level * 4
            if len(nodes) == 1:
                pos[nodes[0]] = (0, y)
            else:
                x_spacing = 6
                start_x = -(len(nodes) - 1) * x_spacing / 2
                for i, node in enumerate(nodes):
                    pos[node] = (start_x + i * x_spacing, y)
    else:
        pos = nx.spring_layout(G, k=3, iterations=50)
    
    return pos

pos = simple_layout(G, roots)

# Obtener etiquetas limpias + PID
labels = {}
for node in G.nodes():
    label = G.nodes[node]['label']
    clean_label = label.replace('.exe', '').replace('C:\\WINDOWS\\System32\\', '')
    labels[node] = f"{clean_label}\n(PID: {node})"

# Colores simples
node_colors = []
for node in G.nodes():
    label = G.nodes[node]['label']
    if is_very_important(label):
        node_colors.append('lightgreen')
    else:
        node_colors.append('lightblue')

# Visualización limpia y minimalista
plt.figure(figsize=(16, 10))

nx.draw_networkx_nodes(
    G, pos,
    node_size=3000,
    node_color=node_colors,
    alpha=0.9,
    linewidths=2,
    edgecolors="black"
)

nx.draw_networkx_edges(
    G, pos,
    arrows=True,
    arrowsize=25,
    edge_color="darkgray",
    width=2,
    alpha=0.8,
    arrowstyle="->"
)

nx.draw_networkx_labels(
    G, pos,
    labels=labels,
    font_size=8,          # Texto más pequeño
    font_weight="bold"
)

plt.title("Procesos Más Importantes del Sistema", fontsize=14, fontweight="bold", pad=20)  # Título más pequeño
plt.axis("off")
plt.tight_layout()

# Leyenda simple
if any(is_very_important(G.nodes[n]['label']) for n in G.nodes()):
    legend_elements = [
        plt.Circle((0,0), 0.1, color='lightgreen', label='Aplicaciones importantes'),
        plt.Circle((0,0), 0.1, color='lightblue', label='Procesos del sistema')
    ]
    plt.legend(handles=legend_elements, loc='upper right', fontsize=10)  # Leyenda más pequeña

# Info mínima
info_text = f"Mostrando {len(G.nodes())} procesos más relevantes"
plt.figtext(0.02, 0.02, info_text, fontsize=8, style='italic')  # Texto de info más pequeño
plt.savefig("grafico_pstree.png", dpi=300, bbox_inches='tight')

plt.show()

# Estadísticas finales
print(f"\nProcesos mostrados:")
important_count = 0
system_count = 0

for node in G.nodes():
    label = G.nodes[node]['label']
    print(f"  - {label}")
    if is_very_important(label):
        important_count += 1
    else:
        system_count += 1

print(f"\nResumen:")
print(f"  Aplicaciones importantes: {important_count}")
print(f"  Procesos del sistema: {system_count}")
print(f"  Total: {len(G.nodes())}")
