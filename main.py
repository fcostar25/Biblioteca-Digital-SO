"""
Escenarios concurrentes: dos clientes (hilos) piden la ÚLTIMA copia de un libro.

Uso (desde la carpeta del proyecto):
    python3 src/main.py                  # los 4 escenarios
    python3 src/main.py basico           # tipo básico sin sincronización
    python3 src/main.py basico-mutex     # tipo básico con mutex
    python3 src/main.py complejo         # tipo complejo sin sincronización
    python3 src/main.py complejo-mutex   # tipo complejo con mutex
"""

import sys
import threading

from biblioteca_basica import BibliotecaBasica, BibliotecaBasicaMutex
from biblioteca_compleja import BibliotecaCompleja, BibliotecaComplejaMutex

LIBRO = "El Principito"

INVENTARIO = {
    "El Principito": {"total": 3, "disponibles": 1},          # queda la última copia
    "Cien años de soledad": {"total": 2, "disponibles": 2},
}


# Clase Cliente: cada cliente es un hilo
class Cliente(threading.Thread):
    """Hilo que pide prestado un libro a la biblioteca COMPARTIDA."""

    def __init__(self, nombre, biblioteca, titulo=None):
        super().__init__(name=nombre)
        self.nombre = nombre
        self.biblioteca = biblioteca   # MISMA instancia para todos los hilos
        self.titulo = titulo           # solo se usa en el tipo complejo
        self.resultado = None          # True si recibió el libro

    def run(self):
        if self.titulo is None:
            # Tipo básico: la biblioteca maneja un solo libro.
            self.resultado = self.biblioteca.prestar(self.nombre)
        else:
            # Tipo complejo: hay que indicar qué libro se pide.
            self.resultado = self.biblioteca.prestar(self.nombre, self.titulo)


# Ejecución de un escenario
def ejecutar(nombre_escenario, biblioteca, titulo=None):
    """Lanza a Ana y Luis sobre la MISMA biblioteca y muestra el resultado."""
    print("=" * 55)
    print(nombre_escenario)
    print("=" * 55)

    if titulo is None:
        inicial = biblioteca.consultar()
    else:
        inicial = biblioteca.consultar(titulo)
    print(f"Copias disponibles de '{LIBRO}' al inicio: {inicial}")

    # Los dos hilos reciben la misma instancia de la biblioteca.
    ana = Cliente("Ana", biblioteca, titulo)
    luis = Cliente("Luis", biblioteca, titulo)

    # Ambos hilos arrancan casi al mismo tiempo...
    ana.start()
    luis.start()

    # ...y el hilo principal espera a que los dos terminen.
    ana.join()
    luis.join()

    # Contar cuántos préstamos fueron aceptados.
    aceptados = 0
    if ana.resultado:
        aceptados = aceptados + 1
    if luis.resultado:
        aceptados = aceptados + 1

    if titulo is None:
        final = biblioteca.consultar()
    else:
        final = biblioteca.consultar(titulo)

    print(f"Préstamos aceptados: {aceptados} de 2")
    print(f"Copias disponibles al final: {final}")

    if titulo is not None:
        print(f"Historial: {biblioteca.historial}")

    if biblioteca.es_consistente():
        print("Resultado: CONSISTENTE")
    else:
        print("Resultado: INCONSISTENTE (condición de carrera)")
    print()


# Escenarios
def escenario_basico():
    biblioteca = BibliotecaBasica(LIBRO, copias=1)
    ejecutar("BÁSICO (int) - sin sincronización", biblioteca)


def escenario_basico_mutex():
    biblioteca = BibliotecaBasicaMutex(LIBRO, copias=1)
    ejecutar("BÁSICO (int) - con mutex", biblioteca)


def escenario_complejo():
    biblioteca = BibliotecaCompleja(INVENTARIO)
    ejecutar("COMPLEJO (dict + list) - sin sincronización", biblioteca, LIBRO)


def escenario_complejo_mutex():
    biblioteca = BibliotecaComplejaMutex(INVENTARIO)
    ejecutar("COMPLEJO (dict + list) - con mutex", biblioteca, LIBRO)


# PUNTO DE ENTRADA
escenario_basico()
escenario_basico_mutex()
escenario_complejo()
escenario_complejo_mutex()
