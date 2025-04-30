# Generador de Grafo Dirigido desde Archivos de Ubicaciones y Usuarios

Este proyecto permite crear un **grafo dirigido** utilizando datos de ubicación y relaciones entre usuarios, usando `NetworkX` y `Polars`. Posteriormente, guarda el grafo en un archivo binario `.pkl` para ser reutilizado o analizado más adelante.

---

## Requisitos

Antes de ejecutar el código, asegúrate de tener instaladas las siguientes bibliotecas:

pip install networkx polars

Estructura esperada de los archivos de entrada para las ubicaciones:
latitud_1,longitud_1
latitud_2,longitud_2
...
Estructura esperada de los archivos de entrada de los ususarios:
2,4,10
1,5
3
Instrucciones:
Asegúrarse de que los archivos 10_million_location.txt y 10_million_user.txt estén en el mismo directorio.
Ejecutar el script. 


