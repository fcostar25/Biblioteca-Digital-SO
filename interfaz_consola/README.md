# Interfaz por consola

Menú interactivo para configurar, ejecutar y visualizar las 4 versiones de la
solución concurrente (básico/complejo, con y sin mutex).

## Cómo ejecutar

Requiere Python 3.8+, sin dependencias externas. Desde la carpeta del proyecto:

```bash
python interfaz_consola/consola.py
```

## Menú

| Opción | Acción |
|---|---|
| 1 | Básico (int) sin sincronización |
| 2 | Básico (int) con mutex |
| 3 | Complejo (dict + list) sin sincronización |
| 4 | Complejo (dict + list) con mutex |
| 5 | Comparar los 4 escenarios (N corridas) |
| 6 | Restablecer parámetros por defecto |
| 0 | Salir |

Antes de ejecutar un escenario se pueden modificar sus parámetros (Enter mantiene
el valor actual):

- **Básico:** copias disponibles, número de hilos que piden prestado y demora.
- **Complejo:** total y disponibles de cada libro, número de hilos que prestan,
  devuelven y consultan, y demora.

## Qué se muestra

1. **Estado inicial** del recurso y la lista de hilos.
2. **Ejecución en vivo:** el log de cada hilo con su tiempo.
3. **Tabla de hilos:** `Hilo` · `ID` (id del hilo en el SO) · `Operación` ·
   `Antes` · `Resultado` · `Después` · `Observación`. La observación marca
   `!! fuera de rango` y `!! carrera: leyó X, debía quedar Y` cuando un hilo
   trabajó con un valor desactualizado.
4. **Estado final del recurso compartido** con el veredicto
   CONSISTENTE / INCONSISTENTE.

## Archivos

- `consola.py`: menú y lectura de parámetros con validación.
- `vista.py`: colores ANSI y tablas.
- `simulacion.py`, `biblioteca_basica.py`, `biblioteca_compleja.py`, `usuario.py`:
  copias de `src/` con dos cambios: la demora es un parámetro y cada operación
  registra un evento (hilo, operación, antes, resultado, después) para la tabla.
  La lógica de las secciones críticas y del mutex es la misma que en `src/`.

Los colores se desactivan solos si la salida no es una terminal, o si se
define la variable de entorno `NO_COLOR`.
