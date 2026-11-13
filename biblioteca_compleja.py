"""
Recurso compartido con TIPO COMPLEJO: un diccionario (inventario) y una
lista (historial).

    inventario = {
        "El Principito":        {"total": 3, "disponibles": 1},
        "Cien años de soledad": {"total": 2, "disponibles": 2},
    }
    historial = [
        {"usuario": "Ana", "titulo": "El Principito"},
    ]
"""

import sys
import threading
import time

DEMORA = 0.1


def log(mensaje):
    print(mensaje)


# Versión SIN sincronización
class BibliotecaCompleja:
    """Biblioteca cuyo recurso compartido es un dict (inventario) + una list (historial)."""

    def __init__(self, inventario):
        self.inventario = {}                      # RECURSO COMPARTIDO (dict)
        for titulo in inventario:
            datos_libro = inventario[titulo]
            self.inventario[titulo] = {
                "total": datos_libro["total"],
                "disponibles": datos_libro["disponibles"],
            }

        self.historial = []                       # RECURSO COMPARTIDO (list)

    def consultar(self, titulo):
        """Devuelve cuántas copias hay disponibles de un libro (solo lee)."""
        return self.inventario[titulo]["disponibles"]

    def es_consistente(self):
        """Las copias disponibles de cada libro deben estar entre 0 y el total."""
        for titulo in self.inventario:
            libro = self.inventario[titulo]
            if libro["disponibles"] < 0:
                return False
            if libro["disponibles"] > libro["total"]:
                return False
        return True

    def prestar(self, usuario, titulo):
        libro = self.inventario[titulo]

        #  INICIO SECCIÓN CRÍTICA 

        # 1. CONSULTA
        disponibles = libro["disponibles"]
        log(f"{usuario} consulta '{titulo}': {disponibles} de {libro['total']}")

        # 2. VALIDACIÓN
        if disponibles > 0:
            time.sleep(DEMORA)

            # 3. ACTUALIZACIÓN
            libro["disponibles"] = libro["disponibles"] - 1

            # 4. REGISTRO en el historial
            movimiento = {"usuario": usuario, "titulo": titulo}
            self.historial.append(movimiento)

            log(f"{usuario} recibe '{titulo}' -> quedan {libro['disponibles']}")
            prestado = True
        else:
            log(f"{usuario}: rechazado, no hay copias de '{titulo}'")
            prestado = False
        #  FIN SECCIÓN CRÍTICA 

        return prestado


# Versión SINCRONIZADA con mutex (threading.Lock)
class BibliotecaComplejaMutex(BibliotecaCompleja):
    """Misma representación (dict + list), protegida con UN solo mutex."""

    def __init__(self, inventario):
        super().__init__(inventario)
        self.lock = threading.Lock()

    def consultar(self, titulo):
        self.lock.acquire()
        disponibles = self.inventario[titulo]["disponibles"]
        self.lock.release()
        return disponibles

    def prestar(self, usuario, titulo):
        libro = self.inventario[titulo]
        log(f"{usuario} espera el mutex")

        self.lock.acquire() #

        #  INICIO SECCIÓN CRÍTICA 
        # 1. CONSULTA
        disponibles = libro["disponibles"]
        log(f"{usuario} consulta '{titulo}': {disponibles} de {libro['total']}")

        # 2. VALIDACIÓN
        if disponibles > 0:
            time.sleep(DEMORA)        # procesando... los demás esperan

            # 3. ACTUALIZACIÓN
            libro["disponibles"] = libro["disponibles"] - 1

            # 4. REGISTRO en el historial
            movimiento = {"usuario": usuario, "titulo": titulo}
            self.historial.append(movimiento)

            log(f"{usuario} recibe '{titulo}' -> quedan {libro['disponibles']}")
            prestado = True
        else:
            log(f"{usuario}: rechazado, no hay copias de '{titulo}'")
            prestado = False
        #  FIN SECCIÓN CRÍTICA 

        self.lock.release()

        return prestado
