"""
Representación del recurso con TIPO BÁSICO: un número entero (int).

    copias_disponibles = 1      # copias libres de UN libro

- Es sencillo: una sola variable cuenta las copias libres.
- Solo sirve para un libro (diez libros = diez variables).
- No guarda quién pidió el libro (no hay historial).
- No conoce el total de copias, así que no puede validar devoluciones.
"""

import sys
import threading
import time

# --------------------------------------------------
# Tiempo que tarda la biblioteca en procesar una solicitud (validar al
# usuario, generar la licencia, etc.). Ensancha la ventana entre "consultar"
# y "actualizar" para que la condición de carrera aparezca en cada ejecución.
# --------------------------------------------------
DEMORA = 0.1


# ==================================================
# Versión SIN sincronización
# ==================================================
class BibliotecaBasica:
    """Biblioteca cuyo recurso compartido es un entero."""

    def __init__(self, titulo, copias):
        self.titulo = titulo
        self.copias_disponibles = copias  # RECURSO COMPARTIDO (int)
        self.verbose = True
        self._t0 = time.perf_counter()

    # --------------------------
    # Utilidades
    # --------------------------
    def log(self, mensaje):
        """Imprime una línea con el tiempo transcurrido desde el inicio."""
        if self.verbose:
            t = time.perf_counter() - self._t0
            sys.stdout.write(f"[{t:.3f}s] {mensaje}\n")

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

    # ¿QUÉ PUEDE SALIR MAL? Ana y Luis piden la ÚLTIMA copia a la vez:
    #   1. Ana consulta -> 1 copia, pasa la validación y queda procesando.
    #   2. Luis consulta -> sigue habiendo 1 (Ana aún no resta), también pasa.
    #   3. Ana resta -> 0.
    #   4. Luis resta -> -1.
    # Se prestó una copia que no existe y el contador quedó en -1.
    # Consulta + validación + actualización deben ejecutarse como UNA sola
    # operación indivisible: esa es la SECCIÓN CRÍTICA.
    def prestar(self, usuario, titulo):
        if not self._es_mi_libro(usuario, titulo):
            return False

        # ============ INICIO SECCIÓN CRÍTICA ============
        disponibles = self.copias_disponibles                    # 1. CONSULTA
        self.log(f"{usuario} consulta: {disponibles} copia(s) disponible(s)")

        if disponibles > 0:                                      # 2. VALIDACIÓN
            time.sleep(DEMORA)  # procesando... otro hilo puede entrar aquí
            self.copias_disponibles -= 1                         # 3. ACTUALIZACIÓN
            prestado = True
        else:
            prestado = False
        # ============= FIN SECCIÓN CRÍTICA ==============

        if prestado:
            self.log(f"{usuario} recibe el libro -> quedan {self.copias_disponibles}")
        else:
            self.log(f"{usuario}: solicitud rechazada, no hay copias")
        return prestado

    def devolver(self, usuario, titulo):
        if not self._es_mi_libro(usuario, titulo):
            return False

        # ============ INICIO SECCIÓN CRÍTICA ============
        # Leer-modificar-escribir del contador: no es una operación atómica.
        # El int no conoce el total, así que acepta cualquier devolución.
        self.copias_disponibles += 1                             # ACTUALIZACIÓN
        # ============= FIN SECCIÓN CRÍTICA ==============

        self.log(f"{usuario} devuelve el libro -> quedan {self.copias_disponibles}")
        return True


# ==================================================
# Versión SINCRONIZADA con mutex (threading.Lock)
# ==================================================
class BibliotecaBasicaMutex(BibliotecaBasica):
    """Misma representación (int), protegida por un mutex."""

    def __init__(self, titulo, copias):
        super().__init__(titulo, copias)
        # Mutex = una sola llave para el contador. Solo el hilo que la tiene
        # puede consultar, validar y actualizar copias_disponibles; los demás
        # esperan bloqueados hasta que se libere.
        self.lock = threading.Lock()

    def consultar(self, titulo=None):
        # Leer con el lock evita ver un valor a medio actualizar.
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
                time.sleep(DEMORA)  # procesando... los demás esperan
                self.copias_disponibles -= 1                     # 3. ACTUALIZACIÓN
                prestado = True
            else:
                prestado = False
            # ============= FIN SECCIÓN CRÍTICA ==============

            if prestado:
                self.log(f"{usuario} recibe el libro -> quedan {self.copias_disponibles}")
            else:
                self.log(f"{usuario}: solicitud rechazada, no hay copias")
            self.log(f"{usuario} [UNLOCK] sale de la sección crítica")
        # <<< LIBERA el mutex al salir del with (también si ocurre una excepción).

        return prestado

    def devolver(self, usuario, titulo):
        if not self._es_mi_libro(usuario, titulo):
            return False

        # >>> ADQUIERE el mutex
        with self.lock:
            # ============ INICIO SECCIÓN CRÍTICA ============
            self.copias_disponibles += 1                         # ACTUALIZACIÓN
            # ============= FIN SECCIÓN CRÍTICA ==============
            self.log(f"{usuario} devuelve el libro -> quedan {self.copias_disponibles}")
        # <<< LIBERA el mutex
        return True
