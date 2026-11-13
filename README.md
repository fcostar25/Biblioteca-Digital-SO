# Biblioteca-Digital-SO

Integrantes: David Motoche, Fernando Costa

Sistema que administra préstamos y devoluciones de libros digitales, controlando el inventario y el historial de solicitudes de los usuarios.

## Estructura

- `src/biblioteca_basica.py`: recurso como entero (`int`), versión sin sincronización y versión con mutex.
- `src/biblioteca_compleja.py`: recurso como diccionario + lista (`dict` + `list`), versión sin sincronización y versión con mutex.
- `src/usuario.py`: clase `Usuario`, un hilo (`threading.Thread`) por persona.
- `src/simulacion.py`: clase `Simulacion`, los escenarios y la tabla de resultados.
- `evidencias/`: salidas de ejecución (`.txt`) y figuras usadas en el informe.
- `Proyecto_Sistemas.docx`: informe con la sección crítica, la justificación del mutex, la tabla de resultados y las evidencias.

## Cómo ejecutar

Requiere Python 3, sin dependencias externas. Desde la carpeta del proyecto:

```bash
python3 src/simulacion.py                  # todos los escenarios + tabla
python3 src/simulacion.py basico           # tipo básico sin sincronización
python3 src/simulacion.py basico-mutex     # tipo básico con mutex
python3 src/simulacion.py complejo         # tipo complejo sin sincronización
python3 src/simulacion.py complejo-mutex   # tipo complejo con mutex
python3 src/simulacion.py tabla            # 20 corridas por escenario
```
