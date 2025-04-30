# ADA
# Explicación Detallada del Código

Este script de Python está diseñado para construir un grafo a partir de datos de ubicaciones y usuarios, y luego realizar un análisis exploratorio de datos (EDA) básico. Utiliza las bibliotecas `igraph`, `time`, `logging`, `polars`, `pickle`, y `numpy`.

## Importación de Bibliotecas

\`\`\`python
import igraph as ig
import time
import logging
import polars as pl
import pickle
import numpy as np
\`\`\`

* `import igraph as ig`: Importa la biblioteca `igraph`, que se utiliza para crear, manipular y analizar grafos. Se importa con el alias `ig` para facilitar su uso.
* `import time`: Importa el módulo `time` para medir el tiempo de ejecución de diferentes partes del código, lo cual es útil para evaluar el rendimiento.
* `import logging`: Importa el módulo `logging` para registrar mensajes informativos, de advertencia o de error durante la ejecución del programa. Esto ayuda a depurar y monitorear el proceso.
* `import polars as pl`: Importa la biblioteca `polars` para trabajar con DataFrames de manera eficiente, especialmente útil para grandes conjuntos de datos.
* `import pickle`: Importa el módulo `pickle` para serializar y deserializar objetos de Python. En este caso, se utiliza para guardar y cargar el grafo en un archivo.
* `import numpy as np`: Importa la biblioteca `numpy` para trabajar eficientemente con grandes arreglos de datos numéricos, como las coordenadas de las ubicaciones.

## Configuración del Logging

\`\`\`python
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
\`\`\`

* Configura el sistema de registro (logging).
    * `level=logging.INFO`: Establece el nivel mínimo de los mensajes que se van a registrar en `INFO`. Esto significa que se registrarán los mensajes de tipo `INFO`, `WARNING`, `ERROR` y `CRITICAL`.
    * `format='%(asctime)s - %(levelname)s - %(message)s'`: Define el formato de los mensajes de registro.
        * `%(asctime)s`: Fecha y hora del evento.
        * `%(levelname)s`: Nivel del mensaje (por ejemplo, `INFO`, `WARNING`).
        * `%(message)s`: El mensaje descriptivo.

## Función `crear_grafo_igraph(ubicaciones_path, usuarios_path, block_size=4_000_000)`

\`\`\`python
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
\`\`\`

* Esta función crea un grafo dirigido a partir de archivos de ubicaciones y usuarios.
    * `ubicaciones_path`: Ruta al archivo que contiene las ubicaciones de los nodos.
    * `usuarios_path`: Ruta al archivo que contiene las conexiones entre los nodos (quién se conecta con quién).
    * `block_size`: Especifica el número de líneas que se procesarán en un bloque antes de agregar las aristas al grafo. Esto mejora el rendimiento para archivos grandes. Por defecto es 4,000,000.
* `start_time = time.time()`: Guarda el tiempo de inicio para calcular la duración del proceso.
* `logging.info("Cargando ubicaciones...")`: Registra un mensaje informativo.
* `ubicaciones = np.loadtxt(ubicaciones_path, delimiter=',')`: Carga las ubicaciones desde el archivo CSV a un array de NumPy. Se asume que las ubicaciones están en formato de latitud y longitud, separadas por comas.
* `num_nodos = ubicaciones.shape[0]`: Obtiene el número de nodos contando las filas del array de ubicaciones.
* `ubicaciones = [tuple(row) for row in ubicaciones]`: Convierte el array de NumPy a una lista de tuplas, donde cada tupla representa una ubicación (latitud, longitud). Esto es necesario para que `igraph` pueda usar las ubicaciones como atributos de los nodos.
* `logging.info(f"Se cargaron {num_nodos} ubicaciones.")`: Registra el número de ubicaciones cargadas.
* `logging.info("Cargando usuarios y creando aristas (modo robusto y rápido)...")`: Informa que se están cargando los datos de los usuarios y creando las conexiones entre ellos.
* `edges = []`: Inicializa una lista vacía para guardar las aristas del grafo. Cada arista se representará como una tupla `(nodo_origen, nodo_destino)`.
* `with open(usuarios_path, 'r', encoding='utf-8', errors='ignore') as file:`: Abre el archivo de usuarios para leer las conexiones.
    * `'r'`: Abre el archivo en modo lectura.
    * `encoding='utf-8'`: Especifica la codificación de caracteres UTF-8, que es una buena práctica para manejar diferentes tipos de caracteres.
    * `errors='ignore'`: Indica que se deben ignorar los errores de decodificación. Esto es útil si el archivo contiene caracteres no válidos, pero podría resultar en la pérdida de algunos datos.
* `block = []`: Inicializa una lista vacía llamada `block`. Esta lista se utiliza para almacenar temporalmente lotes de aristas antes de agregarlas a la lista `edges`. Esto mejora el rendimiento al reducir la cantidad de veces que se extiende la lista `edges`.
* `for line_number, line in enumerate(file, start=1):`: Itera sobre cada línea del archivo de usuarios.
    * `line_number`: Es el número de línea actual (comenzando desde 1).
    * `line`: Es el contenido de la línea.
* `src = line_number - 1`: Calcula el índice del nodo de origen (`src`) restando 1 al número de línea. Los índices de los nodos comienzan en 0, pero los números de línea comienzan en 1.
* `if not line.strip(): continue`: Salta las líneas vacías.
    * `line.strip()`: Elimina los espacios en blanco al principio y al final de la línea.
    * `if not line.strip()`: Verifica si la línea está vacía después de eliminar los espacios en blanco. Si está vacía, el `continue` hace que el bucle pase a la siguiente línea.
* `if not (0 <= src < num_nodos): continue`: Salta las líneas donde el nodo de origen no es válido.
    * Verifica que el índice del nodo de origen esté dentro del rango válido de nodos (0 a `num_nodos` - 1).
* `conexiones = set()`: Inicializa un conjunto vacío llamado `conexiones`. Se utiliza un conjunto para evitar agregar aristas duplicadas.
* `for x in line.split(','):`: Divide la línea por comas para obtener los IDs de los nodos destino (los nodos a los que el nodo origen se conecta).
    * `line.split(',')`: Divide la línea en una lista de cadenas, utilizando la coma como separador.
* `x = x.strip()`: Elimina los espacios en blanco alrededor del ID del nodo destino.
* `if not x.isdigit(): continue`: Salta los valores que no son números enteros, ya que se espera que los IDs de los nodos sean números.
* `dst = int(x) - 1`: Convierte el ID del nodo destino a un entero y resta 1 para obtener el índice del nodo destino.
* `if 0 <= dst < num_nodos and dst != src:`: Verifica que el nodo destino sea válido y que no sea el mismo que el nodo origen (para evitar auto-conexiones).
    * `0 <= dst < num_nodos`: Verifica que el nodo destino esté dentro del rango válido de nodos.
    * `dst != src`: Verifica que el nodo destino no sea el mismo que el nodo origen.
* `conexiones.add(dst)`: Agrega el índice del nodo destino al conjunto `conexiones`.
* `block.extend((src, dst) for dst in conexiones)`: Agrega las aristas desde el nodo origen (`src`) a todos los nodos destino en `conexiones` al bloque actual. Utiliza una comprensión de lista para crear una lista de tuplas (aristas) y luego extiende el bloque con esas aristas.
* `if (line_number) % block_size == 0:`: Verifica si se ha procesado un número de líneas igual al `block_size`.
    * Si es así, significa que se ha completado un bloque de procesamiento.
* `edges.extend(block)`: Agrega todas las aristas del bloque a la lista principal de aristas (`edges`).
* `block = []`: Reinicia la lista `block` para el siguiente bloque de aristas.
* `if block:`: Después de procesar todas las líneas del archivo, si quedan aristas en el bloque, las agrega a la lista `edges`.
* `logging.info(f"Se procesaron {len(edges)} aristas.")`: Informa el número total de aristas procesadas.
* `g = ig.Graph(directed=True)`: Crea un nuevo grafo dirigido usando `igraph`.
* `g.add_vertices(num_nodos)`: Agrega los nodos al grafo.
* `g.add_edges(edges)`: Agrega las aristas al grafo.
* `g.vs["location"] = ubicaciones`: Asigna las ubicaciones de los nodos como un atributo llamado "location" a los vértices del grafo. `g.vs` se utiliza para acceder a los vértices del grafo.
* `return g`: Devuelve el grafo creado.

## Función `generar_tabla_grafos_ordenados(grafo, num_nodos=50)`

\`\`\`python
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
\`\`\`

* Genera una tabla con información sobre los primeros y últimos nodos del grafo. Esto es útil para obtener una vista rápida de la estructura del grafo.
* `grafo`: El objeto grafo de `igraph`.
* `num_nodos`: El número de primeros y últimos nodos a incluir en la tabla. Por defecto, 50.
* `nodos = list(range(grafo.vcount()))`: Crea una lista con los índices de todos los nodos del grafo. `grafo.vcount()` devuelve el número de nodos.
* `primeros_nodos = nodos[:num_nodos]`: Obtiene los índices de los primeros `num_nodos` nodos.
* `ultimos_nodos = nodos[-num_nodos:]`: Obtiene los índices de los últimos `num_nodos` nodos.
* `nodos_seleccionados = primeros_nodos + ultimos_nodos`: Combina las listas de los primeros y últimos nodos.
* `data = []`: Inicializa una lista vacía para almacenar los datos de la tabla.
* `for idx, nodo in enumerate(nodos_seleccionados, start=1):`: Itera sobre los nodos seleccionados.
    * `idx`: Es el índice de la fila en la tabla (comenzando desde 1).
    * `nodo`: Es el índice del nodo en el grafo.
* `loc = grafo.vs[nodo]["location"]`: Obtiene la ubicación del nodo desde el atributo "location" del vértice. `grafo.vs` se utiliza para acceder a los vértices del grafo.
* `if loc is not None: lat, lon = loc else: lat, lon = None, None`: Obtiene latitud y longitud, si la ubicación existe.
* `conexiones = grafo.successors(nodo)`: Obtiene los nodos a los que el nodo actual se conecta. `grafo.successors(nodo)` devuelve una lista de los índices de los nodos sucesores del nodo dado.
* `num_conexiones = len(conexiones)`: Calcula el número de conexiones del nodo.
* `print(f"Nodo {nodo+1}: Conexiones -> {[c+1 for c in conexiones]}")`: Imprime las conexiones del nodo. Se suma 1 a los índices de los nodos para mostrarlos en base 1.
* `data.append({...})`: Agrega un diccionario a la lista `data` con la información del nodo.
    * `'Index'`: Índice de la fila en la tabla.
    * `'Nodo'`: Índice del nodo (base 1).
    * `'Latitud'`: Latitud del nodo.
    * `'Longitud'`: Longitud del nodo.
    * `'Conexiones'`: Número de conexiones del nodo.
* `tabla = pl.DataFrame(data)`: Crea un DataFrame de Polars a partir de la lista de diccionarios `data`.
* `return tabla`: Devuelve el DataFrame creado.

## Función `realizar_eda(grafo)`

\`\`\`python
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
\`\`\`

* Realiza un Análisis Exploratorio de Datos (EDA) básico en el grafo.
* `grafo`: El objeto grafo de `igraph`.
* `try:`: Inicia un bloque `try` para capturar posibles errores durante el EDA.
* `num_nodos = grafo.vcount()`: Obtiene el número de nodos en el grafo.
* `num_aristas = grafo.ecount()`: Obtiene el número de aristas en el grafo.
* `grados = grafo.degree()`: Obtiene los grados de cada nodo.
* `max_grado = max(grados)`: Calcula el grado máximo.
* `min_grado = min(grados)`: Calcula el grado mínimo.
* `promedio_grado = sum(grados) / num_nodos`: Calcula el grado promedio.
* Las siguientes líneas (`logging.info(...)`) registran los resultados del EDA.
* `except Exception as e:`: Captura cualquier excepción que ocurra durante el EDA.
* `logging.error(f"Error durante el EDA: {e}")`: Registra el error.

## Bloque Principal (`if __name__ == "__main__":`)

\`\`\`python
if __name__ == "__main__":
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
\`\`\`

* Este bloque se ejecuta cuando se corre el script.
* Define las rutas de los archivos de entrada.
* Llama a `crear_grafo_igraph()` para crear el grafo.
* Si el grafo se crea correctamente:
    * Llama a `realizar_eda()` para realizar el EDA.
    * Llama a `generar_tabla_grafos_ordenados()` para obtener la tabla de nodos.
    * Imprime la tabla en la consola.
    * Guarda la tabla en un archivo CSV llamado "tabla\_grafos.csv".

