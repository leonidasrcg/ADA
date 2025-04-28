#pip install networkx polars time pickle
import networkx as nx  # Importa la librería para trabajar con grafos
import polars as pl  # Importa la librería para manejar grandes volúmenes de datos de manera eficiente
import time  # Importa el módulo para medir el tiempo
import pickle  # Para guardar y cargar el grafo en formato binario

def crear_grafo_dirigido_desde_archivos(ubicaciones_path, usuarios_path, output_path):
    try:
        # Inicia el contador de tiempo
        start_time = time.time()

        # Leer ubicaciones completas usando Polars
        print("Cargando ubicaciones...")
        ubicaciones_df = pl.read_csv(ubicaciones_path, has_header=False, new_columns=['lat', 'lon'])
        G = nx.DiGraph()  # Crea un grafo dirigido vacío

        # Itera sobre cada fila del DataFrame y agrega nodos al grafo
        for i, row in enumerate(ubicaciones_df.iter_rows(named=True)):
            G.add_node(i, location=(row['lat'], row['lon']))  # Cada nodo tiene una ubicación (latitud y longitud)

        print(f"Se cargaron {ubicaciones_df.shape[0]} ubicaciones.")  # Muestra cuántas ubicaciones se cargaron

        # Leer usuarios línea por línea usando Polars
        print("Cargando usuarios línea por línea...")
        with open(usuarios_path, 'r') as file:
            for line_number, line in enumerate(file, start=1):
                try:
                    usuario = [int(x) - 1 for x in line.strip().split(',') if x.isdigit()]
                    for j in usuario:
                        G.add_edge(line_number - 1, j)
                except ValueError:
                    print(f"Error al procesar la línea {line_number}. Saltando...")

        print(f"Se procesaron {line_number} líneas de usuarios.")  # Muestra cuántas líneas se procesaron

        # Calcula el tiempo total de ejecución
        end_time = time.time()
        print(f"Tiempo total para cargar el grafo: {end_time - start_time:.2f} segundos.")

        # Guardar el grafo en un archivo
        with open(output_path, 'wb') as f:
            pickle.dump(G, f)
        print(f"Grafo guardado en '{output_path}'.")

        return G  # Devuelve el grafo creado

    except FileNotFoundError as e:
        print(f"Error: Archivo no encontrado - {e}")
        return None
    except ValueError as e:
        print(f"Error: Datos inválidos en los archivos - {e}")
        return None

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

# Define las rutas de los archivos de entrada y salida
ubicaciones_archivo = '10_million_location.txt'
usuarios_archivo = '10_million_user.txt'
grafo_archivo = 'grafo.pkl'  # Archivo donde se guardará el grafo

# Llama a la función para crear el grafo a partir de los archivos
grafo = crear_grafo_dirigido_desde_archivos(ubicaciones_archivo, usuarios_archivo, grafo_archivo)

# Si el grafo se creó correctamente, muestra el número de nodos y aristas
if grafo:
    print(f"Grafo creado con {grafo.number_of_nodes()} nodos y {grafo.number_of_edges()} aristas.")

# Cargar el grafo desde el archivo guardado
grafo_cargado = cargar_grafo_desde_archivo(grafo_archivo)
if grafo_cargado:
    print(f"Grafo cargado con {grafo_cargado.number_of_nodes()} nodos y {grafo_cargado.number_of_edges()} aristas.")