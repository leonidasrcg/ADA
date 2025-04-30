import igraph as ig
import time
import logging
import numpy as np
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def crear_grafo_igraph(ubicaciones_path, usuarios_path, output_path, block_size=5_000_000):
    start_time = time.time()
    logging.info("Cargando ubicaciones...")

    ubicaciones = np.loadtxt(ubicaciones_path, delimiter=',')
    num_nodos = ubicaciones.shape[0]
    ubicaciones = [tuple(row) for row in ubicaciones]
    logging.info(f"Se cargaron {num_nodos} ubicaciones.")

    logging.info("Procesando usuarios y guardando bloques de aristas temporales...")
    temp_files = []
    with open(usuarios_path, 'r', encoding='utf-8', errors='ignore') as file:
        block = []
        block_count = 0
        for line_number, line in enumerate(file, start=1):
            src = line_number - 1
            if not line.strip():
                continue
            if not (0 <= src < num_nodos):
                continue
            conexiones = set()
            for x in line.split(','):
                x = x.strip()
                if not x.isdigit():
                    continue
                dst = int(x) - 1
                if 0 <= dst < num_nodos and dst != src:
                    conexiones.add(dst)
            block.extend((src, dst) for dst in conexiones)
            if len(block) >= block_size:
                temp_file = f"edges_block_{block_count}.npy"
                np.save(temp_file, np.array(block, dtype=np.int32))
                temp_files.append(temp_file)
                block = []
                block_count += 1
        if block:
            temp_file = f"edges_block_{block_count}.npy"
            np.save(temp_file, np.array(block, dtype=np.int32))
            temp_files.append(temp_file)

    logging.info("Cargando bloques temporales y ensamblando el grafo final...")
    all_edges = [np.load(f) for f in temp_files]
    edges = np.concatenate(all_edges, axis=0)

    g = ig.Graph(directed=True)
    g.add_vertices(num_nodos)
    g.add_edges(edges)
    g.vs["location"] = ubicaciones

    g.write_pickle(output_path)
    logging.info(f"Grafo guardado en '{output_path}' (formato igraph pickle).")

    # Limpia archivos temporales
    for f in temp_files:
        try:
            os.remove(f)
        except Exception as e:
            logging.warning(f"No se pudo borrar el archivo temporal {f}: {e}")

    end_time = time.time()
    logging.info(f"Tiempo total para cargar el grafo: {end_time - start_time:.2f} segundos.")
    return g

def cargar_grafo_desde_archivo(input_path):
    g = ig.Graph.Read_Pickle(input_path)
    logging.info(f"Grafo cargado desde '{input_path}'.")
    return g

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

if __name__ == "__main__":
    ubicaciones_archivo = '1_million_location.txt'
    usuarios_archivo = '1_million_user.txt'
    grafo_archivo = 'grafo_igraph.pkl'

    grafo = crear_grafo_igraph(ubicaciones_archivo, usuarios_archivo, grafo_archivo)
    grafo_cargado = cargar_grafo_desde_archivo(grafo_archivo)
    if grafo_cargado:
        realizar_eda(grafo_cargado)