#pip install scipy networkx polars matplotlib

import networkx as nx  # Importa la librería para trabajar con grafos
import polars as pl  # Importa la librería para manejar grandes volúmenes de datos de manera eficiente
import time  # Importa el módulo para medir el tiempo
import matplotlib.pyplot as plt  # Importa la librería para graficar

def crear_grafo_dirigido_desde_archivos(ubicaciones_path, usuarios_path):
    try:
        # Inicia el contador de tiempo
        start_time_ubicaciones = time.time()
        # Leer ubicaciones completas usando Polars
        print("Cargando ubicaciones...")
        # Carga el archivo de ubicaciones como un DataFrame de Polars, sin encabezados y con columnas renombradas
        ubicaciones_df = pl.read_csv(ubicaciones_path, has_header=False, new_columns=['lat', 'lon'])
        G = nx.DiGraph()  # Crea un grafo dirigido vacío

        # Itera sobre cada fila del DataFrame y agrega nodos al grafo
        for i, row in enumerate(ubicaciones_df.iter_rows(named=True)):
            G.add_node(i + 1, location=(row['lat'], row['lon']))  # Cada nodo tiene una ubicación (latitud y longitud)

        end_time_ubicaciones = time.time()
        print(f"Se cargaron {ubicaciones_df.shape[0]} ubicaciones en {end_time_ubicaciones - start_time_ubicaciones:.4f} segundos.")  # Muestra cuántas ubicaciones se cargaron y el tiempo

        # Medir el tiempo de carga de usuarios
        start_time_usuarios = time.time()
        # Leer usuarios línea por línea usando Polars
        print("Cargando usuarios línea por línea...")
        # Abre el archivo de usuarios en modo lectura
        with open(usuarios_path, 'r') as file:
            for line_number, line in enumerate(file, start=1):  # Itera sobre cada línea del archivo
                try:
                    # Divide la línea en columnas, convierte a enteros y ajusta los índices (resta 1)
                    usuario = [int(x) for x in line.strip().split(',') if x.isdigit()]
                    for j in usuario:  # Agrega una arista desde el nodo actual a cada nodo en la lista
                        G.add_edge(line_number, j)
                except ValueError:
                    # Si ocurre un error al procesar la línea, muestra un mensaje y continúa con la siguiente
                    print(f"Error al procesar la línea {line_number}. Saltando...")

        end_time_usuarios = time.time()
        print(f"Se procesaron {line_number} líneas de usuarios en {end_time_usuarios - start_time_usuarios:.4f} segundos.")  # Muestra cuántas líneas se procesaron y el tiempo

        # Calcula el tiempo total de ejecución
        total_time = end_time_usuarios - start_time_ubicaciones
        print(f"Tiempo total para cargar el grafo: {total_time:.4f} segundos.")

        return G  # Devuelve el grafo creado

    except FileNotFoundError as e:
        # Maneja el error si alguno de los archivos no se encuentra
        print(f"Error: Archivo no encontrado - {e}")
        return None
    except ValueError as e:
        # Maneja errores relacionados con datos inválidos en los archivos
        print(f"Error: Datos inválidos en los archivos - {e}")
        return None

def visualizar_grafo_parcial(grafo, num_nodos):
    """
    Visualiza los primeros `num_nodos` nodos y sus relaciones en el grafo.

    Args:
        grafo: Un objeto grafo dirigido de NetworkX.
        num_nodos: Número de nodos a visualizar.
    """
    # Obtén los primeros `num_nodos` nodos del grafo
    subgrafo_nodos = list(grafo.nodes)[:num_nodos]
    subgrafo = grafo.subgraph(subgrafo_nodos)  # Crea un subgrafo con los nodos seleccionados

    # Define la disposición de los nodos
    pos = nx.spring_layout(subgrafo, seed=42)  # Usa un layout para posicionar los nodos

    # Dibuja el subgrafo
    plt.figure(figsize=(12, 12))  # Define el tamaño de la figura
    nx.draw(
        subgrafo,
        pos,
        with_labels=True,
        node_color='lightblue',
        node_size=500,
        font_size=8,
        edge_color='gray',
        arrowsize=10
    )
    plt.title(f"Visualización de los primeros {num_nodos} nodos del grafo")
    plt.show()

# Define las rutas de los archivos de entrada
ubicaciones_archivo = '10_million_location.txt'
usuarios_archivo = '10_million_user.txt'

# Llama a la función para crear el grafo a partir de los archivos
grafo = crear_grafo_dirigido_desde_archivos(ubicaciones_archivo, usuarios_archivo)

# Si el grafo se creó correctamente, muestra el número de nodos y aristas
if grafo:
    print(f"Grafo creado con {grafo.number_of_nodes()} nodos y {grafo.number_of_edges()} aristas.")
    # Visualiza los primeros 1000 nodos del grafo
    visualizar_grafo_parcial(grafo, num_nodos=50)