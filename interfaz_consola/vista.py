"""
Vista: utilidades para mostrar resultados en la consola (colores y tablas).
"""

import os
import re
import sys

_ANSI = re.compile(r"\x1b\[[0-9;]*m")

# Colores solo si la salida es una terminal y el usuario no pidió desactivarlos.
USAR_COLOR = sys.stdout.isatty() and "NO_COLOR" not in os.environ

# Activa los códigos ANSI en la consola de Windows 10/11.
if os.name == "nt":
    os.system("")

# Permite imprimir tildes y símbolos aunque la consola use otra codificación.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass


# --------------------------
# Colores
# --------------------------
def color(texto, codigo):
    return f"\x1b[{codigo}m{texto}\x1b[0m" if USAR_COLOR else str(texto)


def rojo(t):
    return color(t, "31;1")


def verde(t):
    return color(t, "32;1")


def amarillo(t):
    return color(t, "33;1")


def cian(t):
    return color(t, "36")


def gris(t):
    return color(t, "90")


def negrita(t):
    return color(t, "1")


# Un color distinto para cada hilo (se repiten si hay más hilos que colores).
_COLORES_HILO = ["34;1", "36;1", "32;1", "33;1", "35;1", "94;1", "96;1", "92;1"]


def colores_por_hilo(nombres):
    return {n: _COLORES_HILO[i % len(_COLORES_HILO)] for i, n in enumerate(nombres)}


# --------------------------
# Tablas
# --------------------------
def ancho(texto):
    """Ancho visible del texto (sin contar los códigos de color)."""
    return len(_ANSI.sub("", str(texto)))


def tabla(encabezado, filas):
    """Devuelve una tabla con bordes como texto; respeta los colores al alinear."""
    filas = [[str(c) for c in f] for f in filas]
    anchos = [max(ancho(f[i]) for f in [encabezado] + filas) for i in range(len(encabezado))]
    separador = "+-" + "-+-".join("-" * a for a in anchos) + "-+"

    def linea(celdas):
        return "| " + " | ".join(c + " " * (a - ancho(c)) for c, a in zip(celdas, anchos)) + " |"

    lineas = [separador, linea([negrita(e) for e in encabezado]), separador]
    lineas += [linea(f) for f in filas]
    lineas.append(separador)
    return "\n".join(lineas)


# --------------------------
# Visualización de la ejecución de los hilos
# --------------------------
def formato_estado(valor, total):
    """Tipo básico: '1'. Tipo complejo: '1/3' (disponibles/total)."""
    return str(valor) if total is None else f"{valor}/{total}"


def formato_resultado(ev):
    if ev["operacion"] == "consultar":
        return gris(f"LEYÓ {ev['resultado']}")
    aceptado = ev["resultado"]
    if ev["operacion"] == "prestar":
        return verde("ACEPTADO") if aceptado else amarillo("RECHAZADO")
    return verde("ACEPTADA") if aceptado else amarillo("RECHAZADA")


def observacion(ev):
    """Detecta en una fila los síntomas de una condición de carrera."""
    notas = []
    total, despues = ev["total"], ev["despues"]
    if despues < 0 or (total is not None and despues > total):
        notas.append("fuera de rango")
    if ev["resultado"] is True:
        esperado = ev["antes"] + (-1 if ev["operacion"] == "prestar" else 1)
        if despues != esperado:
            notas.append(f"carrera: leyó {ev['antes']}, debía quedar {esperado}")
    return rojo("!! " + "; ".join(notas)) if notas else verde("OK")


def tabla_hilos(eventos, colores):
    """Una fila por hilo, en el orden en que terminaron su operación."""
    encabezado = ["#", "Hilo", "ID", "Operación", "Antes", "Resultado", "Después", "Observación"]
    filas = []
    for i, ev in enumerate(sorted(eventos, key=lambda e: e["t"]), start=1):
        fuera = observacion(ev) != verde("OK")
        despues = formato_estado(ev["despues"], ev["total"])
        filas.append([
            str(i),
            color(ev["hilo"], colores.get(ev["hilo"], "1")),
            str(ev["id"]),
            f"{ev['operacion']} '{ev['titulo']}'",
            formato_estado(ev["antes"], ev["total"]),
            formato_resultado(ev),
            rojo(despues) if fuera else despues,
            observacion(ev),
        ])
    return tabla(encabezado, filas)
