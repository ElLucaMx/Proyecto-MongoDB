# menu.py

from operaciones import insertar_documento, eliminar_documento, actualizar_documento
from consultas import consulta_simple, consulta_array, consulta_embebido, consulta_agrupacion
from db import get_collection

def run_menu():
    coll = get_collection()
    while True:
        print("\n=== MENÚ PRINCIPAL ===")
        print("1) Insertar documento")
        print("2) Eliminar documento")
        print("3) Actualizar documento")
        print("4) Realizar consulta")
        print("5) Salir")
        opcion = input("Elige una opción: ").strip()

        if opcion == "1":
            insertar_menu(coll)
        elif opcion == "2":
            eliminar_menu(coll)
        elif opcion == "3":
            actualizar_menu(coll)
        elif opcion == "4":
            consultas_menu(coll)
        elif opcion == "5":
            print("– ¡Hasta luego!")
            break
        else:
            print("Opción no válida. Intenta de nuevo.")

def insertar_menu(coll):
    # Pedir al usuario los campos necesarios, luego llamar a insertar_documento(coll, datos)
    ...

def eliminar_menu(coll):
    # Pedir criterio de eliminación, luego llamar a eliminar_documento(coll, criterio)
    ...

def actualizar_menu(coll):
    # Pedir criterio + datos nuevos, luego llamar a actualizar_documento(coll, criterio, cambios)
    ...

def consultas_menu(coll):
    print("\n--- CONSULTAS DISPONIBLES ---")
    print("a) Consulta simple")
    print("b) Consulta con arrays")
    print("c) Consulta con documentos embebidos")
    print("d) Consulta de agrupación")
    tipo = input("Elige tipo de consulta [a-d]: ").strip().lower()
    if tipo == "a":
        consulta_simple(coll)
    elif tipo == "b":
        consulta_array(coll)
    elif tipo == "c":
        consulta_embebido(coll)
    elif tipo == "d":
        consulta_agrupacion(coll)
    else:
        print("Opción de consulta no válida.")
