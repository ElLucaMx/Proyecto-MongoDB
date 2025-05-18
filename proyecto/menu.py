# menu.py

import re
from datetime import datetime

from operaciones import insertar_documento
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
            # Lógica de eliminación...
            pass
        elif opcion == "3":
            # Lógica de actualización...
            pass
        elif opcion == "4":
            # Lógica de consultas...
            pass
        elif opcion == "5":
            print("– ¡Hasta luego!")
            break
        else:
            print("❌ Opción no válida. Intenta de nuevo.")

def insertar_menu(coll):
    """
    Solicita al usuario los datos mínimos para crear un documento (plataforma).
    Solo pide: nombre, fecha de fundación y valor en bolsa.
    El usuario puede teclear 'salir' en cualquier momento para cancelar.
    Valida:
     - Nombre no vacío
     - Fecha en formato YYYY-MM-DD
     - Valor en bolsa numérico y positivo
     - No duplicar nombres existentes
    """
    print("\n--- INSERTAR NUEVA PLATAFORMA ---")
    print("Escribe 'salir' en cualquier momento para cancelar.")

    # 1) Nombre
    while True:
        nombre = input("Nombre de la plataforma: ").strip()
        if nombre.lower() == "salir":
            print("⚠️ Inserción cancelada por el usuario.")
            return
        if not nombre:
            print("❌ El nombre no puede estar vacío. Inténtalo de nuevo.")
            continue

        # Verificar si ya existe otra entrada con el mismo nombre (evitar duplicados)
        existente = coll.find_one({"nombre": nombre})
        if existente:
            print(f"❌ Ya existe una plataforma con el nombre '{nombre}'. Elige otro o escribe 'salir' para cancelar.")
            continue

        break

    # 2) Fecha de fundación
    while True:
        fecha_input = input("Fecha de fundación (YYYY-MM-DD): ").strip()
        if fecha_input.lower() == "salir":
            print("⚠️ Inserción cancelada por el usuario.")
            return
        try:
            # Intentamos parsear con datetime para validar formato
            dt = datetime.strptime(fecha_input, "%Y-%m-%d")
            fecha_iso = dt.strftime("%Y-%m-%dT00:00:00Z")
            break
        except ValueError:
            print("❌ Formato de fecha inválido. Debe ser YYYY-MM-DD (ej. 2001-11-15).")

    # 3) Valor en bolsa
    while True:
        valor_str = input("Valor en bolsa (número > 0): ").strip()
        if valor_str.lower() == "salir":
            print("⚠️ Inserción cancelada por el usuario.")
            return
        try:
            valor = float(valor_str)
            if valor <= 0:
                print("❌ El valor debe ser un número mayor que 0.")
                continue
            break
        except ValueError:
            print("❌ Debes introducir un número válido (p.ej. 12345678.90).")

    # Construimos el documento mínimo
    nuevo_doc = {
        "nombre": nombre,
        "fechaFundacion": fecha_iso,
        "valorEnBolsa": valor,
        "exclusivos": [],
        "subempresa": {}
    }

    # Confirmar antes de insertar
    print("\nRevisa el documento a insertar:")
    print(nuevo_doc)
    confirmar = input("¿Confirmar inserción? (s/n): ").strip().lower()
    if confirmar != "s":
        print("⚠️ Inserción cancelada por el usuario.")
        return

    # Llamamos a la función que hace el insert_one
    insertar_documento(coll, nuevo_doc)