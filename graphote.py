import networkx as nx  # Importa la librería para trabajar con grafos
import polars as pl  # Importa la librería para manejar grandes volúmenes de datos de manera eficiente
import time  # Importa el módulo para medir el tiempo

def crear_grafo_dirigido_desde_archivos(ubicaciones_path, usuarios_path):
    try:
        # Inicia el contador de tiempo
        start_time = time.time()

        # Leer ubicaciones completas usando Polars
        print("Cargando ubicaciones...")
        # Carga el archivo de ubicaciones como un DataFrame de Polars, sin encabezados y con columnas renombradas
        ubicaciones_df = pl.read_csv(ubicaciones_path, has_header=False, new_columns=['lat', 'lon'])
        G = nx.DiGraph()  # Crea un grafo dirigido vacío

        # Itera sobre cada fila del DataFrame y agrega nodos al grafo
        for i, row in enumerate(ubicaciones_df.iter_rows(named=True)):
            G.add_node(i, location=(row['lat'], row['lon']))  # Cada nodo tiene una ubicación (latitud y longitud)

        print(f"Se cargaron {ubicaciones_df.shape[0]} ubicaciones.")  # Muestra cuántas ubicaciones se cargaron

        # Leer usuarios línea por línea usando Polars
        print("Cargando usuarios línea por línea...")
        # Abre el archivo de usuarios en modo lectura
        with open(usuarios_path, 'r') as file:
            for line_number, line in enumerate(file, start=1):  # Itera sobre cada línea del archivo
                try:
                    # Divide la línea en columnas, convierte a enteros y ajusta los índices (resta 1)
                    usuario = [int(x) - 1 for x in line.strip().split(',') if x.isdigit()]
                    for j in usuario:  # Agrega una arista desde el nodo actual a cada nodo en la lista
                        G.add_edge(line_number - 1, j)
                except ValueError:
                    # Si ocurre un error al procesar la línea, muestra un mensaje y continúa con la siguiente
                    print(f"Error al procesar la línea {line_number}. Saltando...")

        print(f"Se procesaron {line_number} líneas de usuarios.")  # Muestra cuántas líneas se procesaron

        # Calcula el tiempo total de ejecución
        end_time = time.time()
        print(f"Tiempo total para cargar el grafo: {end_time - start_time:.2f} segundos.")

        return G  # Devuelve el grafo creado

    except FileNotFoundError as e:
        # Maneja el error si alguno de los archivos no se encuentra
        print(f"Error: Archivo no encontrado - {e}")
        return None
    except ValueError as e:
        # Maneja errores relacionados con datos inválidos en los archivos
        print(f"Error: Datos inválidos en los archivos - {e}")
        return None

# Define las rutas de los archivos de entrada
ubicaciones_archivo = '10_million_location.txt'
usuarios_archivo = '10_million_user.txt'

# Llama a la función para crear el grafo a partir de los archivos
grafo = crear_grafo_dirigido_desde_archivos(ubicaciones_archivo, usuarios_archivo)

# Si el grafo se creó correctamente, muestra el número de nodos y aristas
if grafo:
    print(f"Grafo creado con {grafo.number_of_nodes()} nodos y {grafo.number_of_edges()} aristas.")