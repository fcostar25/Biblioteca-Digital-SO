"""
Simulación: arma los escenarios, lanza los hilos y muestra los resultados.

Copia de src/simulacion.py adaptada para la interfaz de consola:
- los escenarios reciben parámetros (copias, número de hilos, demora);
- al terminar se muestra la tabla de hilos (vista.tabla_hilos).
"""

import vista
from biblioteca_basica import BibliotecaBasica, BibliotecaBasicaMutex
from biblioteca_compleja import BibliotecaCompleja, BibliotecaComplejaMutex
from usuario import Usuario

REPETICIONES = 20
MAX_HILOS = 12

NOMBRES = ["Ana", "Luis", "Carlos", "María", "Sofía", "Pedro",
           "Lucía", "Jorge", "Elena", "Diego", "Valeria", "Andrés"]

LIBRO_PRESTAMO = "El Principito"
LIBRO_DEVOLUCION = "Cien años de soledad"

# Parámetros por defecto: los mismos escenarios de src/simulacion.py.
PARAMS_BASICO = {
    "copias": 1,          # copias disponibles de 'El Principito'
    "prestamos": 2,       # hilos que piden prestado
    "demora": 0.1,
}
PARAMS_COMPLEJO = {
    "principito_total": 3,
    "principito_disp": 1,  # queda la última copia
    "cien_total": 2,
    "cien_disp": 1,        # falta devolver 1 copia
    "prestamos": 2,        # hilos que piden 'El Principito'
    "devoluciones": 2,     # hilos que devuelven 'Cien años de soledad'
    "consultas": 1,        # hilos que solo consultan 'El Principito'
    "demora": 0.1,
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
        colores = vista.colores_por_hilo([u.nombre for u in self.usuarios])

        if b.verbose:
            print()
            print(vista.cian("=" * 78))
            print(vista.negrita(self.nombre))
            print(vista.cian("=" * 78))
            print(vista.negrita("Estado inicial del recurso:"))
            print(_sangrar(b.estado()))
            print(vista.negrita("Hilos:"))
            for u in self.usuarios:
                print(f"  - {vista.color(u.nombre, colores[u.nombre])}: {u.accion} '{u.titulo}'")
            print()
            print(vista.negrita("Ejecución en vivo:"))

        # Todos los hilos arrancan casi al mismo tiempo...
        for u in self.usuarios:
            u.start()
        # ...y el hilo principal espera a que terminen.
        for u in self.usuarios:
            u.join()

        resumen = self._resumir(iniciales)

        if b.verbose:
            print()
            print(vista.negrita("Visualización de la ejecución de los hilos:"))
            print(vista.tabla_hilos(b.eventos, colores))
            print(vista.gris("Antes/Después = copias disponibles"
                             + ("" if isinstance(b, BibliotecaBasica) else " / total")
                             + " que vio el hilo antes y después de su operación."))
            print()
            print(vista.negrita("Estado final del recurso compartido:"))
            print(_sangrar(b.estado()))
            print()
            for op in resumen["operaciones"]:
                texto = _veredicto(op)
                print(vista.verde(texto) if op["consistente"] else vista.rojo(texto))
            if resumen["consistente"]:
                print(vista.verde("Resultado: CONSISTENTE"))
            else:
                print(vista.rojo("Resultado: INCONSISTENTE (condición de carrera)"))
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
def escenario_basico(con_mutex, verbose=True, params=None):
    """Tipo básico: varios hilos piden la(s) copia(s) de 'El Principito'."""
    p = {**PARAMS_BASICO, **(params or {})}
    clase = BibliotecaBasicaMutex if con_mutex else BibliotecaBasica
    biblioteca = clase(LIBRO_PRESTAMO, copias=p["copias"], demora=p["demora"])
    biblioteca.verbose = verbose
    usuarios = [Usuario(NOMBRES[i], biblioteca, LIBRO_PRESTAMO, "prestar")
                for i in range(p["prestamos"])]
    version = "con mutex" if con_mutex else "sin sincronización"
    return Simulacion(f"TIPO BÁSICO (int) - {version}", biblioteca, usuarios)


def escenario_complejo(con_mutex, verbose=True, params=None):
    """Tipo complejo: carrera de préstamos, de devoluciones y consultas."""
    p = {**PARAMS_COMPLEJO, **(params or {})}
    inventario = {
        LIBRO_PRESTAMO: {"total": p["principito_total"], "disponibles": p["principito_disp"]},
        LIBRO_DEVOLUCION: {"total": p["cien_total"], "disponibles": p["cien_disp"]},
    }
    clase = BibliotecaComplejaMutex if con_mutex else BibliotecaCompleja
    biblioteca = clase(inventario, demora=p["demora"])
    biblioteca.verbose = verbose

    acciones = (["prestar"] * p["prestamos"] + ["devolver"] * p["devoluciones"]
                + ["consultar"] * p["consultas"])
    usuarios = []
    for i, accion in enumerate(acciones):
        titulo = LIBRO_DEVOLUCION if accion == "devolver" else LIBRO_PRESTAMO
        usuarios.append(Usuario(NOMBRES[i], biblioteca, titulo, accion))
    version = "con mutex" if con_mutex else "sin sincronización"
    return Simulacion(f"TIPO COMPLEJO (dict + list) - {version}", biblioteca, usuarios)


# ==================================================
# Tabla comparativa de los 4 escenarios
# ==================================================
def tabla(repeticiones=REPETICIONES, params_basico=None, params_complejo=None):
    """Repite cada escenario y cuenta en cuántas corridas el recurso quedó inconsistente."""
    configuraciones = [
        ("Básico (int)", False, escenario_basico, params_basico),
        ("Básico (int)", True, escenario_basico, params_basico),
        ("Complejo (dict+list)", False, escenario_complejo, params_complejo),
        ("Complejo (dict+list)", True, escenario_complejo, params_complejo),
    ]
    encabezado = ["Representación", "Versión", "Operación", "Inicial",
                  "Solicitudes", "Aceptadas", "Final", "Inconsistentes"]
    filas = []

    for representacion, con_mutex, crear, params in configuraciones:
        corridas = [crear(con_mutex, verbose=False, params=params).ejecutar()
                    for _ in range(repeticiones)]
        for i, op in enumerate(corridas[0]["operaciones"]):
            inconsistentes = sum(1 for c in corridas if not c["operaciones"][i]["consistente"])
            operacion = "Préstamo" if op["accion"] == "prestar" else "Devolución"
            marca = f"{inconsistentes}/{repeticiones}"
            filas.append([
                representacion,
                vista.verde("Mutex") if con_mutex else vista.amarillo("Sin sincronizar"),
                f"{operacion} '{op['titulo']}'",
                str(op["inicial"]),
                str(op["solicitudes"]),
                str(op["aceptadas"]),
                str(op["final"]),
                vista.rojo(marca) if inconsistentes else vista.verde(marca),
            ])

    print(vista.negrita(f"TABLA COMPARATIVA ({repeticiones} corridas por escenario)"))
    print(vista.tabla(encabezado, filas))
    print(vista.gris("Inicial/Final = copias disponibles antes y después (de la primera corrida)."))
    print(vista.gris("Inconsistentes = corridas en que las copias quedaron fuera de rango (< 0 o > total)."))
    return filas
