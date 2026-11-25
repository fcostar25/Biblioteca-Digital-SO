"""
Representación del recurso con TIPO COMPLEJO: diccionario + lista.

    inventario = {"El Principito": {"total": 3, "disponibles": 1}, ...}
    historial  = [{"usuario": "Ana", "titulo": "El Principito", "accion": "préstamo"}]

Copia de src/biblioteca_compleja.py adaptada para la interfaz de consola:
- la demora es un parámetro del constructor;
- cada operación guarda un EVENTO para la tabla de hilos.
"""

import sys
import threading
import time

DEMORA = 0.1


# ==================================================
# Versión SIN sincronización
# ==================================================
class BibliotecaCompleja:
    """Biblioteca cuyo recurso compartido es un dict (inventario) + list (historial)."""

    def __init__(self, inventario, demora=DEMORA):
        # Copia propia para que cada simulación empiece desde el mismo estado.
        self.inventario = {t: dict(d) for t, d in inventario.items()}  # RECURSO COMPARTIDO
        self.historial = []                                            # RECURSO COMPARTIDO
        self.demora = demora
        self.verbose = True
        self.eventos = []
        self._t0 = time.perf_counter()

    # --------------------------
    # Utilidades
    # --------------------------
    def log(self, mensaje):
        if self.verbose:
            t = time.perf_counter() - self._t0
            sys.stdout.write(f"  [{t:.3f}s] {mensaje}\n")

    def total(self, titulo):
        return self.inventario[titulo]["total"]

    def registrar_evento(self, usuario, operacion, titulo, antes, resultado, despues):
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
        return self.inventario[titulo]["disponibles"]

    def prestar(self, usuario, titulo):
        if not self._existe(usuario, titulo):
            return False

        # ============ INICIO SECCIÓN CRÍTICA ============
        libro = self.inventario[titulo]
        disponibles = libro["disponibles"]                       # 1. CONSULTA
        self.log(f"{usuario} consulta '{titulo}': {disponibles} copia(s) disponible(s)")

        if disponibles > 0:                                      # 2. VALIDACIÓN
            time.sleep(self.demora)  # procesando... otro hilo puede entrar aquí
            libro["disponibles"] -= 1                            # 3. ACTUALIZACIÓN
            self._registrar(usuario, titulo, "préstamo")         # 4. REGISTRO
            prestado = True
        else:
            prestado = False
        despues = libro["disponibles"]
        # ============= FIN SECCIÓN CRÍTICA ==============

        self.registrar_evento(usuario, "prestar", titulo, disponibles, prestado, despues)
        if prestado:
            self.log(f"{usuario} recibe '{titulo}' -> quedan {despues}")
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
            time.sleep(self.demora)  # procesando... otro hilo puede entrar aquí
            libro["disponibles"] += 1                            # 3. ACTUALIZACIÓN
            self._registrar(usuario, titulo, "devolución")       # 4. REGISTRO
            devuelto = True
        else:
            devuelto = False
        despues = libro["disponibles"]
        # ============= FIN SECCIÓN CRÍTICA ==============

        self.registrar_evento(usuario, "devolver", titulo, disponibles, devuelto, despues)
        if devuelto:
            self.log(f"{usuario} devuelve '{titulo}' -> quedan {despues}")
        else:
            self.log(f"{usuario}: devolución de '{titulo}' rechazada, no falta ninguna copia")
        return devuelto


# ==================================================
# Versión SINCRONIZADA con mutex (threading.Lock)
# ==================================================
class BibliotecaComplejaMutex(BibliotecaCompleja):
    """Misma representación (dict + list), protegida por UN solo mutex."""

    def __init__(self, inventario, demora=DEMORA):
        super().__init__(inventario, demora)
        # Un solo mutex protege TODO el recurso: inventario e historial.
        self.lock = threading.Lock()

    def consultar(self, titulo):
        with self.lock:
            return self.inventario[titulo]["disponibles"]

    def prestar(self, usuario, titulo):
        if not self._existe(usuario, titulo):
            return False

        self.log(f"{usuario} pide '{titulo}' y espera el mutex")

        with self.lock:
            self.log(f"{usuario} [LOCK] entra a la sección crítica")

            # ============ INICIO SECCIÓN CRÍTICA ============
            libro = self.inventario[titulo]
            disponibles = libro["disponibles"]                   # 1. CONSULTA
            self.log(f"{usuario} consulta '{titulo}': {disponibles} copia(s) disponible(s)")

            if disponibles > 0:                                  # 2. VALIDACIÓN
                time.sleep(self.demora)  # procesando... los demás esperan
                libro["disponibles"] -= 1                        # 3. ACTUALIZACIÓN
                self._registrar(usuario, titulo, "préstamo")     # 4. REGISTRO
                prestado = True
            else:
                prestado = False
            despues = libro["disponibles"]
            # ============= FIN SECCIÓN CRÍTICA ==============

            self.registrar_evento(usuario, "prestar", titulo, disponibles, prestado, despues)
            if prestado:
                self.log(f"{usuario} recibe '{titulo}' -> quedan {despues}")
            else:
                self.log(f"{usuario}: préstamo de '{titulo}' rechazado, no hay copias")
            self.log(f"{usuario} [UNLOCK] sale de la sección crítica")

        return prestado

    def devolver(self, usuario, titulo):
        if not self._existe(usuario, titulo):
            return False

        self.log(f"{usuario} quiere devolver '{titulo}' y espera el mutex")

        with self.lock:
            self.log(f"{usuario} [LOCK] entra a la sección crítica")

            # ============ INICIO SECCIÓN CRÍTICA ============
            libro = self.inventario[titulo]
            disponibles = libro["disponibles"]                   # 1. CONSULTA
            self.log(f"{usuario} consulta '{titulo}': {disponibles} de {libro['total']} disponible(s)")

            if disponibles < libro["total"]:                     # 2. VALIDACIÓN
                time.sleep(self.demora)  # procesando... los demás esperan
                libro["disponibles"] += 1                        # 3. ACTUALIZACIÓN
                self._registrar(usuario, titulo, "devolución")   # 4. REGISTRO
                devuelto = True
            else:
                devuelto = False
            despues = libro["disponibles"]
            # ============= FIN SECCIÓN CRÍTICA ==============

            self.registrar_evento(usuario, "devolver", titulo, disponibles, devuelto, despues)
            if devuelto:
                self.log(f"{usuario} devuelve '{titulo}' -> quedan {despues}")
            else:
                self.log(f"{usuario}: devolución de '{titulo}' rechazada, no falta ninguna copia")
            self.log(f"{usuario} [UNLOCK] sale de la sección crítica")

        return devuelto
