"""
Interfaz por consola de la Biblioteca Digital concurrente.

Menú interactivo para seleccionar uno de los 4 escenarios, ingresar sus
parámetros, ejecutarlo y ver la ejecución de cada hilo y el estado final.

Uso (desde la carpeta del proyecto):
    python interfaz_consola/consola.py
"""

import simulacion as sim
import vista

# Parámetros actuales: empiezan con los valores por defecto y se recuerdan
# entre una ejecución y otra.
params_basico = dict(sim.PARAMS_BASICO)
params_complejo = dict(sim.PARAMS_COMPLEJO)

OPCIONES = {
    "1": ("Básico (int) - sin sincronización", sim.escenario_basico, False),
    "2": ("Básico (int) - con mutex", sim.escenario_basico, True),
    "3": ("Complejo (dict + list) - sin sincronización", sim.escenario_complejo, False),
    "4": ("Complejo (dict + list) - con mutex", sim.escenario_complejo, True),
}


# --------------------------
# Lectura de datos con validación
# --------------------------
def pedir_entero(mensaje, defecto, minimo=0, maximo=None):
    while True:
        texto = input(f"  {mensaje} [{defecto}]: ").strip()
        if texto == "":
            return defecto
        try:
            valor = int(texto)
        except ValueError:
            print(vista.rojo("    Debe ser un número entero."))
            continue
        if valor < minimo or (maximo is not None and valor > maximo):
            rango = f"entre {minimo} y {maximo}" if maximo is not None else f"mayor o igual a {minimo}"
            print(vista.rojo(f"    El valor debe estar {rango}."))
            continue
        return valor


def pedir_decimal(mensaje, defecto, minimo=0.0, maximo=2.0):
    while True:
        texto = input(f"  {mensaje} [{defecto}]: ").strip().replace(",", ".")
        if texto == "":
            return defecto
        try:
            valor = float(texto)
        except ValueError:
            print(vista.rojo("    Debe ser un número (ej. 0.1)."))
            continue
        if not minimo <= valor <= maximo:
            print(vista.rojo(f"    El valor debe estar entre {minimo} y {maximo}."))
            continue
        return valor


def pedir_si_no(mensaje, defecto=False):
    sufijo = "S/n" if defecto else "s/N"
    while True:
        texto = input(f"{mensaje} ({sufijo}): ").strip().lower()
        if texto == "":
            return defecto
        if texto in ("s", "si", "sí"):
            return True
        if texto in ("n", "no"):
            return False
        print(vista.rojo("  Responda s o n."))


# --------------------------
# Parámetros de cada tipo de recurso
# --------------------------
def mostrar_parametros_basico(p):
    return (f"{p['copias']} copia(s) de '{sim.LIBRO_PRESTAMO}', "
            f"{p['prestamos']} hilo(s) que piden prestado, demora {p['demora']} s")


def mostrar_parametros_complejo(p):
    return (f"'{sim.LIBRO_PRESTAMO}' {p['principito_disp']}/{p['principito_total']}, "
            f"'{sim.LIBRO_DEVOLUCION}' {p['cien_disp']}/{p['cien_total']}, "
            f"hilos: {p['prestamos']} préstamo(s), {p['devoluciones']} devolución(es), "
            f"{p['consultas']} consulta(s), demora {p['demora']} s")


def editar_basico(p):
    print(vista.gris("  (Enter mantiene el valor entre corchetes)"))
    p["copias"] = pedir_entero(f"Copias disponibles de '{sim.LIBRO_PRESTAMO}'", p["copias"], 0, 100)
    p["prestamos"] = pedir_entero("Número de hilos que piden prestado", p["prestamos"], 1, sim.MAX_HILOS)
    p["demora"] = pedir_decimal("Demora de procesamiento en segundos", p["demora"])


def editar_complejo(p):
    print(vista.gris("  (Enter mantiene el valor entre corchetes)"))
    p["principito_total"] = pedir_entero(f"Total de copias de '{sim.LIBRO_PRESTAMO}'",
                                         p["principito_total"], 1, 100)
    p["principito_disp"] = pedir_entero(f"Copias disponibles de '{sim.LIBRO_PRESTAMO}'",
                                        min(p["principito_disp"], p["principito_total"]),
                                        0, p["principito_total"])
    p["cien_total"] = pedir_entero(f"Total de copias de '{sim.LIBRO_DEVOLUCION}'",
                                   p["cien_total"], 1, 100)
    p["cien_disp"] = pedir_entero(f"Copias disponibles de '{sim.LIBRO_DEVOLUCION}'",
                                  min(p["cien_disp"], p["cien_total"]), 0, p["cien_total"])
    while True:
        p["prestamos"] = pedir_entero(f"Hilos que piden prestado '{sim.LIBRO_PRESTAMO}'",
                                      p["prestamos"], 0, sim.MAX_HILOS)
        p["devoluciones"] = pedir_entero(f"Hilos que devuelven '{sim.LIBRO_DEVOLUCION}'",
                                         p["devoluciones"], 0, sim.MAX_HILOS)
        p["consultas"] = pedir_entero(f"Hilos que solo consultan '{sim.LIBRO_PRESTAMO}'",
                                      p["consultas"], 0, sim.MAX_HILOS)
        total = p["prestamos"] + p["devoluciones"] + p["consultas"]
        if 1 <= total <= sim.MAX_HILOS:
            break
        print(vista.rojo(f"    El total de hilos debe estar entre 1 y {sim.MAX_HILOS} (hay {total})."))
    p["demora"] = pedir_decimal("Demora de procesamiento en segundos", p["demora"])


# --------------------------
# Acciones del menú
# --------------------------
def ejecutar_escenario(opcion):
    nombre, crear, con_mutex = OPCIONES[opcion]
    es_basico = crear is sim.escenario_basico
    params = params_basico if es_basico else params_complejo

    print()
    print(vista.negrita(f"Escenario: {nombre}"))
    print("Parámetros actuales: "
          + (mostrar_parametros_basico(params) if es_basico else mostrar_parametros_complejo(params)))
    if pedir_si_no("¿Desea modificar los parámetros?"):
        (editar_basico if es_basico else editar_complejo)(params)

    crear(con_mutex, verbose=True, params=params).ejecutar()


def comparar_escenarios():
    print()
    print(vista.negrita("Comparar los 4 escenarios"))
    print("  Básico:   " + mostrar_parametros_basico(params_basico))
    print("  Complejo: " + mostrar_parametros_complejo(params_complejo))
    n = pedir_entero("Número de corridas por escenario", sim.REPETICIONES, 1, 200)
    print(vista.gris("  Ejecutando... (puede tardar unos segundos)"))
    print()
    sim.tabla(n, params_basico, params_complejo)


def restablecer():
    params_basico.clear()
    params_basico.update(sim.PARAMS_BASICO)
    params_complejo.clear()
    params_complejo.update(sim.PARAMS_COMPLEJO)
    print(vista.verde("Parámetros restablecidos a los valores por defecto."))


def mostrar_menu():
    print()
    print(vista.cian("+" + "-" * 62 + "+"))
    print(vista.cian("|") + vista.negrita("  BIBLIOTECA DIGITAL SO - Simulador de concurrencia".ljust(62))
          + vista.cian("|"))
    print(vista.cian("+" + "-" * 62 + "+"))
    for clave, (nombre, _, con_mutex) in OPCIONES.items():
        etiqueta = vista.verde("con mutex") if con_mutex else vista.rojo("sin sincronización")
        tipo = nombre.split(" - ")[0]
        print(f"  [{clave}] {tipo.ljust(24)} {etiqueta}")
    print("  [5] Comparar los 4 escenarios (N corridas)")
    print("  [6] Restablecer parámetros por defecto")
    print("  [0] Salir")


def main():
    while True:
        mostrar_menu()
        opcion = input("\nElija una opción: ").strip()
        if opcion in OPCIONES:
            ejecutar_escenario(opcion)
        elif opcion == "5":
            comparar_escenarios()
        elif opcion == "6":
            restablecer()
        elif opcion == "0":
            print("Hasta luego.")
            return
        else:
            print(vista.rojo("Opción no válida."))
            continue
        input(vista.gris("\nPresione Enter para volver al menú..."))


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nHasta luego.")
