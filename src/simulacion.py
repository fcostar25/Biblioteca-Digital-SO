"""
Simulación: arma los escenarios, lanza los hilos y muestra los resultados.

Uso (desde la carpeta del proyecto):
    python3 src/simulacion.py                  # todos los escenarios + tabla
    python3 src/simulacion.py basico           # tipo básico sin sincronización
    python3 src/simulacion.py basico-mutex     # tipo básico con mutex
    python3 src/simulacion.py complejo         # tipo complejo sin sincronización
    python3 src/simulacion.py complejo-mutex   # tipo complejo con mutex
    python3 src/simulacion.py tabla            # tabla de resultados (20 corridas)
"""

import argparse

from biblioteca_basica import BibliotecaBasica, BibliotecaBasicaMutex
from biblioteca_compleja import BibliotecaCompleja, BibliotecaComplejaMutex
from usuario import Usuario

REPETICIONES = 20

# Estado inicial del tipo complejo: ya hay copias prestadas antes de empezar.
INVENTARIO_INICIAL = {
    "El Principito": {"total": 3, "disponibles": 1},         # queda la última copia
    "Cien años de soledad": {"total": 2, "disponibles": 1},  # falta devolver 1 copia
}


# ==================================================
# Clase Simulacion
# ==================================================
class Simulacion:
    """Crea el escenario: una sola biblioteca compartida y varios usuarios (hilos)."""

    def __init__(self, nombre, biblioteca, usuarios):
        self.nombre = nombre
        self.biblioteca = biblioteca
        self.usuarios = usuarios

    def ejecutar(self):
        """Inicia todos los hilos, espera a que terminen y devuelve un resumen."""
        b = self.biblioteca
        titulos = list(dict.fromkeys(u.titulo for u in self.usuarios))
        iniciales = {t: b.consultar(t) for t in titulos}

        if b.verbose:
            print("=" * 66)
            print(self.nombre)
            print("=" * 66)
            print("Estado inicial:")
            print(_sangrar(b.estado()))
            print("Hilos:")
            for u in self.usuarios:
                print(f"  - {u.nombre}: {u.accion} '{u.titulo}'")
            print()

        # Todos los hilos arrancan casi al mismo tiempo...
        for u in self.usuarios:
            u.start()
        # ...y el hilo principal espera a que terminen.
        for u in self.usuarios:
            u.join()

        resumen = self._resumir(iniciales)

        if b.verbose:
            print()
            print("Estado final:")
            print(_sangrar(b.estado()))
            print()
            for op in resumen["operaciones"]:
                print(_veredicto(op))
            print("Resultado:", "CONSISTENTE" if resumen["consistente"]
                  else "INCONSISTENTE (condición de carrera)")
        return resumen

    def _resumir(self, iniciales):
        b = self.biblioteca
        operaciones = []
        for accion in ("prestar", "devolver"):
            for titulo in iniciales:
                hilos = [u for u in self.usuarios
                         if u.accion == accion and u.titulo == titulo]
                if not hilos:
                    continue
                operaciones.append({
                    "accion": accion,
                    "titulo": titulo,
                    "inicial": iniciales[titulo],
                    "solicitudes": len(hilos),
                    "aceptadas": sum(1 for u in hilos if u.resultado),
                    "final": b.consultar(titulo),
                    "consistente": b.es_consistente(titulo),
                })
        return {
            "nombre": self.nombre,
            "operaciones": operaciones,
            "consistente": b.es_consistente(),
        }


def _sangrar(texto):
    return "\n".join("  " + linea for linea in texto.splitlines())


def _veredicto(op):
    t, ac, sol, ini, fin = op["titulo"], op["aceptadas"], op["solicitudes"], op["inicial"], op["final"]
    if op["consistente"]:
        verbo = ("préstamo(s) aceptado(s)" if op["accion"] == "prestar"
                 else "devolución(es) aceptada(s)")
        return f"OK: '{t}' -> {ac} de {sol} {verbo}, quedan {fin} disponible(s)."
    if op["accion"] == "prestar":
        return (f"ERROR: se prestaron {ac} copia(s) de '{t}' cuando solo había {ini} "
                f"disponible(s); el contador quedó en {fin}.")
    return (f"ERROR: se aceptaron {ac} devoluciones de '{t}' y quedaron {fin} "
            f"copias disponibles, más de las que existen.")


# ==================================================
# Escenarios
# ==================================================
def escenario_basico(con_mutex, verbose=True):
    """Tipo básico: Ana y Luis piden la ÚLTIMA copia de 'El Principito'."""
    clase = BibliotecaBasicaMutex if con_mutex else BibliotecaBasica
    biblioteca = clase("El Principito", copias=1)  # UNA sola instancia compartida
    biblioteca.verbose = verbose
    usuarios = [
        Usuario("Ana", biblioteca, "El Principito", "prestar"),
        Usuario("Luis", biblioteca, "El Principito", "prestar"),
    ]
    version = "con mutex" if con_mutex else "sin sincronización"
    return Simulacion(f"TIPO BÁSICO (int) - {version}", biblioteca, usuarios)


def escenario_complejo(con_mutex, verbose=True):
    """Tipo complejo: carrera por la última copia y carrera de devoluciones."""
    clase = BibliotecaComplejaMutex if con_mutex else BibliotecaCompleja
    biblioteca = clase(INVENTARIO_INICIAL)  # UNA sola instancia compartida
    biblioteca.verbose = verbose
    usuarios = [
        Usuario("Ana", biblioteca, "El Principito", "prestar"),
        Usuario("Luis", biblioteca, "El Principito", "prestar"),
        Usuario("Carlos", biblioteca, "Cien años de soledad", "devolver"),
        Usuario("María", biblioteca, "Cien años de soledad", "devolver"),
        Usuario("Sofía", biblioteca, "El Principito", "consultar"),
    ]
    version = "con mutex" if con_mutex else "sin sincronización"
    return Simulacion(f"TIPO COMPLEJO (dict + list) - {version}", biblioteca, usuarios)


ESCENARIOS = {
    "basico": lambda: escenario_basico(con_mutex=False),
    "basico-mutex": lambda: escenario_basico(con_mutex=True),
    "complejo": lambda: escenario_complejo(con_mutex=False),
    "complejo-mutex": lambda: escenario_complejo(con_mutex=True),
}


# ==================================================
# Tabla de resultados
# ==================================================
def tabla(repeticiones=REPETICIONES):
    """Repite cada escenario y cuenta en cuántas corridas el recurso quedó inconsistente."""
    configuraciones = [
        ("Básico (int)", False, escenario_basico),
        ("Básico (int)", True, escenario_basico),
        ("Complejo (dict+list)", False, escenario_complejo),
        ("Complejo (dict+list)", True, escenario_complejo),
    ]
    encabezado = ["Representación", "Versión", "Operación", "Inicial",
                  "Solicitudes", "Aceptadas", "Final", "Inconsistentes"]
    filas = []

    for representacion, con_mutex, crear in configuraciones:
        corridas = [crear(con_mutex, verbose=False).ejecutar() for _ in range(repeticiones)]
        for i, op in enumerate(corridas[0]["operaciones"]):
            inconsistentes = sum(1 for c in corridas if not c["operaciones"][i]["consistente"])
            operacion = "Préstamo" if op["accion"] == "prestar" else "Devolución"
            filas.append([
                representacion,
                "Mutex" if con_mutex else "Sin sincronizar",
                f"{operacion} '{op['titulo']}'",
                str(op["inicial"]),
                str(op["solicitudes"]),
                str(op["aceptadas"]),
                str(op["final"]),
                f"{inconsistentes}/{repeticiones}",
            ])

    anchos = [max(len(f[i]) for f in [encabezado] + filas) for i in range(len(encabezado))]
    separador = "+-" + "-+-".join("-" * a for a in anchos) + "-+"

    def linea(celdas):
        return "| " + " | ".join(c.ljust(a) for c, a in zip(celdas, anchos)) + " |"

    print(f"TABLA DE RESULTADOS ({repeticiones} corridas por escenario)")
    print(separador)
    print(linea(encabezado))
    print(separador)
    for f in filas:
        print(linea(f))
    print(separador)
    print("Inicial/Final = copias disponibles antes y después de la simulación.")
    print("Inconsistentes = corridas en que las copias quedaron fuera de rango (< 0 o > total).")
    return filas


# =========================
# Función main
# =========================
def main():
    parser = argparse.ArgumentParser(description="Simulación concurrente de la biblioteca digital")
    parser.add_argument("escenario", nargs="?", default="todo",
                        choices=[*ESCENARIOS, "tabla", "todo"])
    parser.add_argument("-n", "--repeticiones", type=int, default=REPETICIONES,
                        help="corridas por escenario para la tabla")
    args = parser.parse_args()

    if args.escenario in ESCENARIOS:
        ESCENARIOS[args.escenario]().ejecutar()
    elif args.escenario == "tabla":
        tabla(args.repeticiones)
    else:
        for crear in ESCENARIOS.values():
            crear().ejecutar()
            print()
        tabla(args.repeticiones)


# =========================
# PUNTO DE ENTRADA
# =========================
if __name__ == "__main__":
    main()
