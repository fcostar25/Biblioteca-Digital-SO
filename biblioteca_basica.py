"""
Recurso compartido con TIPO BÁSICO: un número entero.

    copias = 1   # copias disponibles de UN libro
"""

import sys
import threading
import time

DEMORA = 0.1


def log(mensaje):
    print(mensaje)


# Versión SIN sincronización

class BibliotecaBasica:
    def __init__(self, titulo, copias):
        self.titulo = titulo
        self.copias = copias          # RECURSO COMPARTIDO (int)

    def consultar(self):
        return self.copias

    def prestar(self, usuario):
        #INICIO SECCIÓN CRÍTICA
        # 1. CONSULTA
        disponibles = self.copias
        log(f"{usuario} consulta: {disponibles} copia(s) disponible(s)")

        # 2. VALIDACIÓN
        if disponibles > 0:
            time.sleep(DEMORA)

            # 3. ACTUALIZACIÓN
            self.copias -= 1
            log(f"{usuario} recibe '{self.titulo}' -> quedan {self.copias}")
            prestado = True
        else:
            log(f"{usuario}: rechazado, no hay copias")
            prestado = False
        #  FIN SECCIÓN CRÍTICA 

        return prestado

    def es_consistente(self):
        """El número de copias nunca debería ser negativo."""
        if self.copias >= 0:
            return True
        else:
            return False
        

#Con mutex (threading.Lock)
class BibliotecaBasicaMutex(BibliotecaBasica):
    """Misma representación (int), protegida con un mutex."""

    def __init__(self, titulo, copias):
        super().__init__(titulo, copias)
        self.lock = threading.Lock()

    def consultar(self):
        self.lock.acquire()
        disponibles = self.copias
        self.lock.release()
        return disponibles

    def prestar(self, usuario):
        log(f"{usuario} espera el mutex")

        self.lock.acquire()

        # Inicio de Seccion Critica
        # 1. CONSULTA
        disponibles = self.copias
        log(f"{usuario} consulta: {disponibles} copia(s) disponible(s)")

        # 2. VALIDACIÓN
        if disponibles > 0:
            time.sleep(DEMORA)        
            # 3. ACTUALIZACIÓN
            self.copias = self.copias - 1
            log(f"{usuario} recibe '{self.titulo}' -> quedan {self.copias}")
            prestado = True
        else:
            log(f"{usuario}: rechazado, no hay copias")
            prestado = False
        # Fin de seccion Critica

        self.lock.release()

        return prestado
