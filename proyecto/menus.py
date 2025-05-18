from db import get_collection
from cons_simples import consulta_simple_menu
from cons_arrays import consulta_array
from cons_embebidos import consulta_embebido
from cons_agrupacion import consulta_agrupacion
from operaciones_menu import insertar_menu as run_insertar_menu
from operaciones_menu import eliminar_menu as run_eliminar_menu
from operaciones_menu import actualizar_menu as run_actualizar_menu


def run_menu():
    salir = False
    coll = get_collection()

    while not salir:
        print("\n=== MENÚ PRINCIPAL ===")
        print("1) Insertar documento")
        print("2) Eliminar documento")
        print("3) Actualizar documento")
        print("4) Realizar consulta")
        print("5) Salir")
        opcion = input("Elige una opción: ").strip()

        if opcion == "1":
            run_insertar_menu(coll)
        elif opcion == "2":
            run_eliminar_menu(coll)
        elif opcion == "3":
            run_actualizar_menu(coll)
        elif opcion == "4":
            consultas_menu(coll)
        elif opcion == "5":
            print("– ¡Hasta luego!")
            salir = True
        else:
            print("Opción no válida. Intenta de nuevo.")


def consultas_menu(coll):
    """
    Submenú para que el usuario elija qué tipo de consulta desea ejecutar.
    1) Consulta simple
    2) Consulta con arrays
    3) Consulta con documentos embebidos
    4) Consulta de agrupación
    5) Volver al menú principal
    """

    print("\n--- MENÚ DE CONSULTAS ---")
    print("1) Consulta simple")
    print("2) Consulta con arrays")
    print("3) Consulta con documentos embebidos")
    print("4) Consulta de agrupación")
    print("5) Volver al menú principal")

    elec = input("Elige una opción [1-5]: ").strip()
    if elec == "1":
        consulta_simple_menu(coll)
    elif elec == "2":
        consulta_array(coll)
    elif elec == "3":
        consulta_embebido(coll)
    elif elec == "4":
        consulta_agrupacion(coll)
    elif elec == "5":
        print("Volviendo al menú principal.")
    else:
        print("Opción de consulta no válida.")
