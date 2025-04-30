import igraph as ig
import time
import logging
import polars as pl
import pickle
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def crear_grafo_igraph(ubicaciones_path, usuarios_path, block_size=4_000_000):
    start_time = time.time()
    logging.info("Cargando ubicaciones...")

    ubicaciones = np.loadtxt(ubicaciones_path, delimiter=',')
    num_nodos = ubicaciones.shape[0]
    ubicaciones = [tuple(row) for row in ubicaciones]
    logging.info(f"Se cargaron {num_nodos} ubicaciones.")

    logging.info("Cargando usuarios y creando aristas (modo robusto y rápido)...")
    edges = []
    with open(usuarios_path, 'r', encoding='utf-8', errors='ignore') as file:
        block = []
        for line_number, line in enumerate(file, start=1):
            src = line_number - 1
            # Salta líneas vacías o con solo espacios
            if not line.strip():
                continue
            # Solo procesa si el nodo fuente es válido
            if not (0 <= src < num_nodos):
                continue
            conexiones = set()
            for x in line.split(','):
                x = x.strip()
                if not x.isdigit():
                    continue
                dst = int(x) - 1
                # Solo agrega si el destino es válido y no es un self-loop
                if 0 <= dst < num_nodos and dst != src:
                    conexiones.add(dst)
            block.extend((src, dst) for dst in conexiones)
            if (line_number) % block_size == 0:
                edges.extend(block)
                block = []
        if block:
            edges.extend(block)
    logging.info(f"Se procesaron {len(edges)} aristas.")

    g = ig.Graph(directed=True)
    g.add_vertices(num_nodos)
    g.add_edges(edges)
    g.vs["location"] = ubicaciones

    return g

def generar_tabla_grafos_ordenados(grafo, num_nodos=50):
    """
    Genera una tabla con información de los primeros y últimos nodos del grafo.
    """
    nodos = list(range(grafo.vcount()))
    primeros_nodos = nodos[:num_nodos]
    ultimos_nodos = nodos[-num_nodos:]
    nodos_seleccionados = primeros_nodos + ultimos_nodos

    data = []
    for idx, nodo in enumerate(nodos_seleccionados, start=1):
        loc = grafo.vs[nodo]["location"]
        if loc is not None:
            lat, lon = loc
        else:
            lat, lon = None, None
        conexiones = grafo.successors(nodo)
        num_conexiones = len(conexiones)
        print(f"Nodo {nodo+1}: Conexiones -> {[c+1 for c in conexiones]}")  # Mostrar base 1
        data.append({
            'Index': idx,
            'Nodo': nodo + 1,  # Mostrar base 1
            'Latitud': lat,
            'Longitud': lon,
            'Conexiones': num_conexiones
        })
    tabla = pl.DataFrame(data)
    return tabla
    

def realizar_eda(grafo):
    try:
        num_nodos = grafo.vcount()
        num_aristas = grafo.ecount()
        grados = grafo.degree()
        max_grado = max(grados)
        min_grado = min(grados)
        promedio_grado = sum(grados) / num_nodos

        logging.info(f"Número de nodos: {num_nodos}")
        logging.info(f"Número de aristas: {num_aristas}")
        logging.info(f"Grado máximo: {max_grado}")
        logging.info(f"Grado mínimo: {min_grado}")
        logging.info(f"Grado promedio: {promedio_grado:.2f}")
    except Exception as e:
        logging.error(f"Error durante el EDA: {e}")

# Define las rutas de los archivos de entrada y salida
ubicaciones_archivo = '10_million_location.txt'
usuarios_archivo = '10_million_user.txt'

# Crear el grafo
grafo = crear_grafo_igraph(ubicaciones_archivo, usuarios_archivo)

# Cargar el grafo desde el archivo guardado
if grafo:
    realizar_eda(grafo)
    tabla_grafos = generar_tabla_grafos_ordenados(grafo, num_nodos=50)
    print(tabla_grafos)
    tabla_grafos.write_csv('tabla_grafos.csv')
    print("Tabla guardada en 'tabla_grafos.csv'.")