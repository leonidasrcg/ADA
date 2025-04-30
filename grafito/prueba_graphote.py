import igraph as ig
import polars as pl  # Para crear y manejar la tabla

def cargar_grafo_desde_archivo(input_path):
    """
    Carga un grafo de igraph desde un archivo pickle.
    """
    g = ig.Graph.Read_Pickle(input_path)
    print(f"Grafo cargado desde '{input_path}'.")
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
        data.append({
            'Index': idx,
            'Nodo': nodo + 1,  # Mostrar base 1
            'Latitud': lat,
            'Longitud': lon,
            'Conexiones': num_conexiones
        })
    tabla = pl.DataFrame(data)
    return tabla

# Ruta del archivo del grafo
grafo_archivo = 'grafo_igraph.pkl'

# Cargar el grafo desde el archivo
grafo = cargar_grafo_desde_archivo(grafo_archivo)

if grafo:
    tabla_grafos = generar_tabla_grafos_ordenados(grafo, num_nodos=50)
    print(tabla_grafos)
    tabla_grafos.write_csv('tabla_grafos.csv')
    print("Tabla guardada en 'tabla_grafos.csv'.")