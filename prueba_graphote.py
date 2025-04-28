import networkx as nx
import pickle
import random
import polars as pl  # Para crear y manejar la tabla

def cargar_grafo_desde_archivo(input_path):
    """
    Carga un grafo desde un archivo previamente guardado.

    Args:
        input_path (str): Ruta del archivo donde se guardó el grafo.

    Returns:
        nx.DiGraph: El grafo cargado.
    """
    try:
        with open(input_path, 'rb') as f:
            G = pickle.load(f)
        print(f"Grafo cargado desde '{input_path}'.")
        return G
    except FileNotFoundError as e:
        print(f"Error: Archivo no encontrado - {e}")
        return None

def generar_tabla_grafos_random(grafo, num_grafos=100):
    """
    Genera una tabla con información de 100 nodos seleccionados aleatoriamente.

    Args:
        grafo (nx.DiGraph): El grafo cargado.
        num_grafos (int): Número de nodos a seleccionar aleatoriamente.

    Returns:
        pd.DataFrame: DataFrame con la información de los nodos seleccionados.
    """
    # Seleccionar nodos aleatorios
    nodos_random = random.sample(list(grafo.nodes), min(num_grafos, grafo.number_of_nodes()))
    
    # Crear una lista para almacenar la información
    data = []
    for idx, nodo in enumerate(nodos_random, start=1):
        lat, lon = grafo.nodes[nodo].get('location', (None, None))
        conexiones = len(list(grafo.successors(nodo)))  # Número de conexiones salientes
        data.append({
            'Grafo #': idx,
            'Latitud': lat,
            'Longitud': lon,
            'Conexiones': conexiones
        })
    
    # Crear un DataFrame con la información
    tabla = pl.DataFrame(data)
    return tabla

# Ruta del archivo del grafo
grafo_archivo = 'grafo.pkl'

# Cargar el grafo desde el archivo
grafo = cargar_grafo_desde_archivo(grafo_archivo)

if grafo:
    # Generar la tabla con 100 nodos aleatorios
    tabla_grafos = generar_tabla_grafos_random(grafo, num_grafos=100)
    
    # Mostrar la tabla
    print(tabla_grafos)
    
    # Guardar la tabla en un archivo CSV
    tabla_grafos.write_csv('tabla_grafos.csv')
    print("Tabla guardada en 'tabla_grafos.csv'.")