"""
Representación del recurso con TIPO BÁSICO: un número entero (int).

    copias_disponibles = 1      # copias libres de UN libro

Copia de src/biblioteca_basica.py adaptada para la interfaz de consola:
- la demora es un parámetro del constructor (antes era una constante fija);
- cada operación guarda un EVENTO (hilo, operación, estado antes, resultado,
  estado después) para poder mostrarlo en la tabla de hilos.
"""

import sys
import threading
import time

# Tiempo que tarda la biblioteca en procesar una solicitud. Ensancha la ventana
# entre "consultar" y "actualizar" para que la condición de carrera aparezca.
DEMORA = 0.1


# ==================================================
# Versión SIN sincronización
# ==================================================
class BibliotecaBasica:
    """Biblioteca cuyo recurso compartido es un entero."""

    def __init__(self, titulo, copias, demora=DEMORA):
        self.titulo = titulo
        self.copias_disponibles = copias  # RECURSO COMPARTIDO (int)
        self.demora = demora
        self.verbose = True
        self.eventos = []                 # registro de operaciones para la vista
        self._t0 = time.perf_counter()

    # --------------------------
    # Utilidades
    # --------------------------
    def log(self, mensaje):
        """Imprime una línea con el tiempo transcurrido desde el inicio."""
        if self.verbose:
            t = time.perf_counter() - self._t0
            sys.stdout.write(f"  [{t:.3f}s] {mensaje}\n")

    def total(self, titulo=None):
        """El int no conoce el total de copias."""
        return None

    def registrar_evento(self, usuario, operacion, titulo, antes, resultado, despues):
        """Guarda lo que hizo un hilo. list.append es atómico en CPython."""
        self.eventos.append({
            "t": time.perf_counter() - self._t0,
            "hilo": usuario,
            "id": threading.get_native_id(),
            "operacion": operacion,
            "titulo": titulo,
            "antes": antes,
            "resultado": resultado,
            "despues": despues,
            "total": self.total(titulo),
        })

    def _es_mi_libro(self, usuario, titulo):
        if titulo != self.titulo:
            self.log(f"{usuario}: '{titulo}' no existe en esta biblioteca")
            return False
        return True

    def es_consistente(self, titulo=None):
        """El contador nunca debería quedar negativo."""
        return self.copias_disponibles >= 0

    def estado(self):
        return f"'{self.titulo}': {self.copias_disponibles} copia(s) disponible(s)"

    # --------------------------
    # Operaciones de los usuarios
    # --------------------------
    def consultar(self, titulo=None):
        # Solo lee el recurso, no lo modifica.
        return self.copias_disponibles

    def prestar(self, usuario, titulo):
        if not self._es_mi_libro(usuario, titulo):
            return False

        # ============ INICIO SECCIÓN CRÍTICA ============
        disponibles = self.copias_disponibles                    # 1. CONSULTA
        self.log(f"{usuario} consulta: {disponibles} copia(s) disponible(s)")

        if disponibles > 0:                                      # 2. VALIDACIÓN
            time.sleep(self.demora)  # procesando... otro hilo puede entrar aquí
            self.copias_disponibles -= 1                         # 3. ACTUALIZACIÓN
            prestado = True
        else:
            prestado = False
        despues = self.copias_disponibles
        # ============= FIN SECCIÓN CRÍTICA ==============

        self.registrar_evento(usuario, "prestar", titulo, disponibles, prestado, despues)
        if prestado:
            self.log(f"{usuario} recibe el libro -> quedan {despues}")
        else:
            self.log(f"{usuario}: solicitud rechazada, no hay copias")
        return prestado

    def devolver(self, usuario, titulo):
        if not self._es_mi_libro(usuario, titulo):
            return False

        # ============ INICIO SECCIÓN CRÍTICA ============
        antes = self.copias_disponibles
        self.copias_disponibles += 1                             # ACTUALIZACIÓN
        despues = self.copias_disponibles
        # ============= FIN SECCIÓN CRÍTICA ==============

        self.registrar_evento(usuario, "devolver", titulo, antes, True, despues)
        self.log(f"{usuario} devuelve el libro -> quedan {despues}")
        return True


# ==================================================
# Versión SINCRONIZADA con mutex (threading.Lock)
# ==================================================
class BibliotecaBasicaMutex(BibliotecaBasica):
    """Misma representación (int), protegida por un mutex."""

    def __init__(self, titulo, copias, demora=DEMORA):
        super().__init__(titulo, copias, demora)
        self.lock = threading.Lock()

    def consultar(self, titulo=None):
        with self.lock:
            return self.copias_disponibles

    def prestar(self, usuario, titulo):
        if not self._es_mi_libro(usuario, titulo):
            return False

        self.log(f"{usuario} pide el libro y espera el mutex")

        # >>> ADQUIERE el mutex: si otro hilo lo tiene, este hilo se bloquea aquí.
        with self.lock:
            self.log(f"{usuario} [LOCK] entra a la sección crítica")

            # ============ INICIO SECCIÓN CRÍTICA ============
            disponibles = self.copias_disponibles                # 1. CONSULTA
            self.log(f"{usuario} consulta: {disponibles} copia(s) disponible(s)")

            if disponibles > 0:                                  # 2. VALIDACIÓN
                time.sleep(self.demora)  # procesando... los demás esperan
                self.copias_disponibles -= 1                     # 3. ACTUALIZACIÓN
                prestado = True
            else:
                prestado = False
            despues = self.copias_disponibles
            # ============= FIN SECCIÓN CRÍTICA ==============

            self.registrar_evento(usuario, "prestar", titulo, disponibles, prestado, despues)
            if prestado:
                self.log(f"{usuario} recibe el libro -> quedan {despues}")
            else:
                self.log(f"{usuario}: solicitud rechazada, no hay copias")
            self.log(f"{usuario} [UNLOCK] sale de la sección crítica")
        # <<< LIBERA el mutex al salir del with.

        return prestado

    def devolver(self, usuario, titulo):
        if not self._es_mi_libro(usuario, titulo):
            return False

        with self.lock:
            # ============ INICIO SECCIÓN CRÍTICA ============
            antes = self.copias_disponibles
            self.copias_disponibles += 1                         # ACTUALIZACIÓN
            despues = self.copias_disponibles
            # ============= FIN SECCIÓN CRÍTICA ==============
            self.registrar_evento(usuario, "devolver", titulo, antes, True, despues)
            self.log(f"{usuario} devuelve el libro -> quedan {despues}")
        return True
