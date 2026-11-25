"""
Usuario: cada persona que usa la biblioteca es un hilo.
Copia de src/usuario.py; la consulta también registra su evento.
"""

import threading


class Usuario(threading.Thread):
    """Hilo que realiza una operación sobre la biblioteca COMPARTIDA."""

    ACCIONES = ("prestar", "devolver", "consultar")

    def __init__(self, nombre, biblioteca, titulo, accion):
        super().__init__(name=nombre)
        if accion not in self.ACCIONES:
            raise ValueError(f"Acción desconocida: {accion}")
        self.nombre = nombre
        self.biblioteca = biblioteca  # misma instancia para todos los hilos
        self.titulo = titulo
        self.accion = accion
        self.resultado = None  # True/False (prestar, devolver) o int (consultar)

    def run(self):
        if self.accion == "prestar":
            self.resultado = self.biblioteca.prestar(self.nombre, self.titulo)
        elif self.accion == "devolver":
            self.resultado = self.biblioteca.devolver(self.nombre, self.titulo)
        else:
            valor = self.biblioteca.consultar(self.titulo)
            self.resultado = valor
            self.biblioteca.registrar_evento(
                self.nombre, "consultar", self.titulo, valor, valor, valor
            )
            self.biblioteca.log(
                f"{self.nombre} consulta '{self.titulo}': {valor} copia(s) disponible(s)"
            )
