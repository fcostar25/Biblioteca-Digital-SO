"""
Representación del recurso con TIPO COMPLEJO: diccionario + lista.

    inventario = {
        "El Principito":        {"total": 3, "disponibles": 1},
        "Cien años de soledad": {"total": 2, "disponibles": 1},
    }
    historial = [
        {"usuario": "Ana", "titulo": "El Principito", "accion": "préstamo"},
    ]

- Maneja todos los libros en una sola estructura.
- Conoce el total de cada libro, así que puede validar las devoluciones.
- Guarda un historial: quién, qué libro y qué acción.
- Un solo mutex protege inventario e historial a la vez.
"""

import sys
import threading
import time

# --------------------------------------------------
# Tiempo de procesamiento entre "consultar" y "actualizar".
# Ensancha la ventana para que la condición de carrera se vea siempre.
# --------------------------------------------------
DEMORA = 0.1


# ==================================================
# Versión SIN sincronización
# ==================================================
class BibliotecaCompleja:
    """Biblioteca cuyo recurso compartido es un dict (inventario) + list (historial)."""

    def __init__(self, inventario):
        # Copia propia para que cada simulación empiece desde el mismo estado.
        self.inventario = {t: dict(d) for t, d in inventario.items()}  # RECURSO COMPARTIDO
        self.historial = []                                            # RECURSO COMPARTIDO
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

    def _existe(self, usuario, titulo):
        if titulo not in self.inventario:
            self.log(f"{usuario}: '{titulo}' no existe en el inventario")
            return False
        return True

    def _registrar(self, usuario, titulo, accion):
        """Agrega un movimiento al historial. Se llama dentro de la sección crítica."""
        self.historial.append({"usuario": usuario, "titulo": titulo, "accion": accion})

    def es_consistente(self, titulo=None):
        """Las copias disponibles deben estar siempre entre 0 y el total."""
        libros = [self.inventario[titulo]] if titulo else self.inventario.values()
        return all(0 <= l["disponibles"] <= l["total"] for l in libros)

    def estado(self):
        lineas = [
            f"'{t}': {l['disponibles']} de {l['total']} copia(s) disponible(s)"
            for t, l in self.inventario.items()
        ]
        lineas.append(f"Historial ({len(self.historial)} movimiento(s)):")
        lineas += [
            f"  - {h['usuario']}: {h['accion']} de '{h['titulo']}'" for h in self.historial
        ]
        return "\n".join(lineas)

    # --------------------------
    # Operaciones de los usuarios
    # --------------------------
    def consultar(self, titulo):
        # Solo lee el recurso, no lo modifica.
        return self.inventario[titulo]["disponibles"]

    # ¿QUÉ PUEDE SALIR MAL?
    # - Préstamo: Ana y Luis piden la última copia de 'El Principito'. Ambos
    #   consultan 1 antes de que alguno reste, ambos pasan la validación, el
    #   libro queda en -1 y el historial registra 2 préstamos de 1 sola copia.
    # - Devolución: Carlos y María devuelven 'Cien años de soledad' cuando solo
    #   hay 1 copia prestada. Ambos ven 1 < 2, ambos suman y quedan 3 copias
    #   disponibles de un total de 2.
    # Consulta + validación + actualización + registro forman la SECCIÓN CRÍTICA.
    def prestar(self, usuario, titulo):
        if not self._existe(usuario, titulo):
            return False

        # ============ INICIO SECCIÓN CRÍTICA ============
        libro = self.inventario[titulo]
        disponibles = libro["disponibles"]                       # 1. CONSULTA
        self.log(f"{usuario} consulta '{titulo}': {disponibles} copia(s) disponible(s)")

        if disponibles > 0:                                      # 2. VALIDACIÓN
            time.sleep(DEMORA)  # procesando... otro hilo puede entrar aquí
            libro["disponibles"] -= 1                            # 3. ACTUALIZACIÓN
            self._registrar(usuario, titulo, "préstamo")         # 4. REGISTRO
            prestado = True
        else:
            prestado = False
        # ============= FIN SECCIÓN CRÍTICA ==============

        if prestado:
            self.log(f"{usuario} recibe '{titulo}' -> quedan {libro['disponibles']}")
        else:
            self.log(f"{usuario}: préstamo de '{titulo}' rechazado, no hay copias")
        return prestado

    def devolver(self, usuario, titulo):
        if not self._existe(usuario, titulo):
            return False

        # ============ INICIO SECCIÓN CRÍTICA ============
        libro = self.inventario[titulo]
        disponibles = libro["disponibles"]                       # 1. CONSULTA
        self.log(f"{usuario} consulta '{titulo}': {disponibles} de {libro['total']} disponible(s)")

        if disponibles < libro["total"]:                         # 2. VALIDACIÓN
            time.sleep(DEMORA)  # procesando... otro hilo puede entrar aquí
            libro["disponibles"] += 1                            # 3. ACTUALIZACIÓN
            self._registrar(usuario, titulo, "devolución")       # 4. REGISTRO
            devuelto = True
        else:
            devuelto = False
        # ============= FIN SECCIÓN CRÍTICA ==============

        if devuelto:
            self.log(f"{usuario} devuelve '{titulo}' -> quedan {libro['disponibles']}")
        else:
            self.log(f"{usuario}: devolución de '{titulo}' rechazada, no falta ninguna copia")
        return devuelto


# ==================================================
# Versión SINCRONIZADA con mutex (threading.Lock)
# ==================================================
class BibliotecaComplejaMutex(BibliotecaCompleja):
    """Misma representación (dict + list), protegida por UN solo mutex."""

    def __init__(self, inventario):
        super().__init__(inventario)
        # Un solo mutex protege TODO el recurso: inventario e historial.
        # Así un préstamo nunca queda con la copia restada pero sin registrar.
        self.lock = threading.Lock()

    def consultar(self, titulo):
        # Leer con el lock evita ver un valor a medio actualizar.
        with self.lock:
            return self.inventario[titulo]["disponibles"]

    def prestar(self, usuario, titulo):
        if not self._existe(usuario, titulo):
            return False

        self.log(f"{usuario} pide '{titulo}' y espera el mutex")

        # >>> ADQUIERE el mutex: si otro hilo lo tiene, este hilo se bloquea aquí.
        with self.lock:
            self.log(f"{usuario} [LOCK] entra a la sección crítica")

            # ============ INICIO SECCIÓN CRÍTICA ============
            libro = self.inventario[titulo]
            disponibles = libro["disponibles"]                   # 1. CONSULTA
            self.log(f"{usuario} consulta '{titulo}': {disponibles} copia(s) disponible(s)")

            if disponibles > 0:                                  # 2. VALIDACIÓN
                time.sleep(DEMORA)  # procesando... los demás esperan
                libro["disponibles"] -= 1                        # 3. ACTUALIZACIÓN
                self._registrar(usuario, titulo, "préstamo")     # 4. REGISTRO
                prestado = True
            else:
                prestado = False
            # ============= FIN SECCIÓN CRÍTICA ==============

            if prestado:
                self.log(f"{usuario} recibe '{titulo}' -> quedan {libro['disponibles']}")
            else:
                self.log(f"{usuario}: préstamo de '{titulo}' rechazado, no hay copias")
            self.log(f"{usuario} [UNLOCK] sale de la sección crítica")
        # <<< LIBERA el mutex al salir del with (también si ocurre una excepción).

        return prestado

    def devolver(self, usuario, titulo):
        if not self._existe(usuario, titulo):
            return False

        self.log(f"{usuario} quiere devolver '{titulo}' y espera el mutex")

        # >>> ADQUIERE el mutex
        with self.lock:
            self.log(f"{usuario} [LOCK] entra a la sección crítica")

            # ============ INICIO SECCIÓN CRÍTICA ============
            libro = self.inventario[titulo]
            disponibles = libro["disponibles"]                   # 1. CONSULTA
            self.log(f"{usuario} consulta '{titulo}': {disponibles} de {libro['total']} disponible(s)")

            if disponibles < libro["total"]:                     # 2. VALIDACIÓN
                time.sleep(DEMORA)  # procesando... los demás esperan
                libro["disponibles"] += 1                        # 3. ACTUALIZACIÓN
                self._registrar(usuario, titulo, "devolución")   # 4. REGISTRO
                devuelto = True
            else:
                devuelto = False
            # ============= FIN SECCIÓN CRÍTICA ==============

            if devuelto:
                self.log(f"{usuario} devuelve '{titulo}' -> quedan {libro['disponibles']}")
            else:
                self.log(f"{usuario}: devolución de '{titulo}' rechazada, no falta ninguna copia")
            self.log(f"{usuario} [UNLOCK] sale de la sección crítica")
        # <<< LIBERA el mutex

        return devuelto
