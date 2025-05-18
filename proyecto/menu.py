# menu.py

import re
from datetime import datetime
import json
from bson import ObjectId
from operaciones import insertar_documento, eliminar_uno, eliminar_varios, actualizar_uno
from consultas import consulta_simple_menu, consulta_array, consulta_embebido, consulta_agrupacion

from db import get_collection

def run_menu():
    salir=False
    coll = get_collection()

    while salir==False:
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
            salir=True
        else:
            print("❌ Opción no válida. Intenta de nuevo.")

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
        print("🔙 Volviendo al menú principal.")
        return
    else:
        print("❌ Opción de consulta no válida.")

def actualizar_menu(coll):
    """
    Pasos:
    1) Obtiene todos los nombres existentes en la colección.
    2) Muestra la lista enumerada de nombres.
    3) El usuario escribe el nombre EXACTO que quiere actualizar (o 'salir' para cancelar).
    4) Si no existe, muestra error y retorna.
    5) Si existe, muestra el documento encontrado (solo _id y nombre) y pregunta qué campo actualizar:
       a) nombre
       b) fechaFundacion
       c) valorEnBolsa
    6) Según elección, pide el nuevo valor (validándolo en cada caso).
    7) Muestra un resumen de la actualización propuesta y pide confirmación (s/n).
    8) Si confirma, llama a actualizar_uno(...) con el filtro correspondiente y el operador $set. Luego imprime resultado.
       Si no confirma, informa que se canceló y retorna.
    """

    print("\n--- ACTUALIZAR DOCUMENTO ---")
    print("Escribe 'salir' en cualquier momento para cancelar.\n")

    # 1) Obtener todos los nombres únicos
    nombres = coll.distinct("nombre")
    if not nombres:
        print("⚠️ La colección está vacía. No hay nada para actualizar.")
        return

    # 2) Mostrar la lista enumerada al usuario
    print("Plataformas disponibles para actualizar:")
    for idx, n in enumerate(sorted(nombres), start=1):
        print(f"  [{idx}]  {n}")
    print()

    # 3) Pedir nombre exacto (o 'salir')
    nombre_input = input("Escribe el nombre EXACTO de la plataforma a actualizar (o 'salir'): ").strip()
    if nombre_input.lower() == "salir":
        print("⚠️ Actualización cancelada por el usuario.")
        return

    if nombre_input not in nombres:
        print(f"❌ El nombre '{nombre_input}' no existe en la base de datos.")
        return

    # 4) Recuperar documento completo para mostrar _id y nombre
    doc = coll.find_one({"nombre": nombre_input})
    if doc is None:
        print("❌ Error inesperado: no se pudo recuperar el documento.")
        return

    _id_str = str(doc.get("_id", "<sin _id>"))
    print(f"\nDocumento seleccionado:")
    print(f"  _id: {_id_str}")
    print(f"  nombre: {doc.get('nombre', '<sin nombre>')}")
    print()

    # 5) Preguntar qué campo actualizar
    print("¿Qué campo deseas actualizar?")
    print("  1) nombre")
    print("  2) fecha de fundación")
    print("  3) valor en bolsa")
    campo_choice = input("Elige 1-3 (o 'salir'): ").strip()
    if campo_choice.lower() == "salir":
        print("⚠️ Actualización cancelada por el usuario.")
        return

    if campo_choice not in ("1", "2", "3"):
        print("❌ Opción de campo inválida. Debe ser 1, 2 ó 3.")
        return

    # 6) Según elección, pedimos y validamos el nuevo valor
    operador_set = {}
    if campo_choice == "1":
        # Actualizar 'nombre'
        nuevo_nombre = input("Nuevo nombre: ").strip()
        if nuevo_nombre.lower() == "salir":
            print("⚠️ Actualización cancelada por el usuario.")
            return
        if not nuevo_nombre:
            print("❌ El nombre no puede quedar vacío.")
            return
        # Comprobar que no exista ya otro con el mismo nombre
        if coll.find_one({"nombre": nuevo_nombre}):
            print(f"❌ Ya existe otra plataforma con el nombre '{nuevo_nombre}'.")
            return
        operador_set = {"$set": {"nombre": nuevo_nombre}}

    elif campo_choice == "2":
        # Actualizar 'fechaFundacion'
        fecha_str = input("Nueva fecha de fundación (YYYY-MM-DD): ").strip()
        if fecha_str.lower() == "salir":
            print("⚠️ Actualización cancelada por el usuario.")
            return
        try:
            dt = datetime.strptime(fecha_str, "%Y-%m-%d")
            nuevo_fecha_iso = dt.strftime("%Y-%m-%dT00:00:00Z")
        except ValueError:
            print("❌ Formato de fecha inválido. Debe ser YYYY-MM-DD.")
            return
        operador_set = {"$set": {"fechaFundacion": nuevo_fecha_iso}}

    else:  # campo_choice == "3"
        # Actualizar 'valorEnBolsa'
        valor_str = input("Nuevo valor en bolsa (número > 0): ").strip()
        if valor_str.lower() == "salir":
            print("⚠️ Actualización cancelada por el usuario.")
            return
        try:
            nuevo_valor = float(valor_str)
            if nuevo_valor <= 0:
                print("❌ El valor debe ser mayor que cero.")
                return
        except ValueError:
            print("❌ Debes introducir un número válido.")
            return
        operador_set = {"$set": {"valorEnBolsa": nuevo_valor}}

    # 7) Mostrar resumen antes de aplicar
    print("\nResumen de la actualización:")
    if campo_choice == "1":
        print(f"  Campo: nombre")
        print(f"  De: {doc.get('nombre')}")
        print(f"  A: {nuevo_nombre}")
    elif campo_choice == "2":
        print(f"  Campo: fechaFundacion")
        print(f"  De: {doc.get('fechaFundacion')}")
        print(f"  A: {nuevo_fecha_iso}")
    else:
        print(f"  Campo: valorEnBolsa")
        print(f"  De: {doc.get('valorEnBolsa')}")
        print(f"  A: {nuevo_valor}")

    confirmar = input("\n¿Confirmar actualización? (s/n): ").strip().lower()
    if confirmar != "s":
        print("⚠️ Actualización cancelada por el usuario.")
        return

    # 8) Llamar a la función que actualiza en MongoDB
    actualizar_uno(coll, {"_id": doc["_id"]}, operador_set)

def eliminar_menu(coll):
    """
    1) Consulta todos los nombres de plataformas existentes.
    2) Los muestra al usuario (enumerados).
    3) El usuario escribe exactamente uno de esos nombres para borrar.
       - Si escribe 'salir', se cancela y vuelve al menú.
       - Si el nombre no está en la lista, se informa y se regresa al menú.
    4) Si existe, muestra el _id y el nombre, pide confirmación (s/n).
       - Si confirma con 's', llama a eliminar_uno(coll, {"nombre": nombre}).
       - Si no, vuelve al menú.
    """

    print("\n--- ELIMINAR DOCUMENTO ---")
    print("Escribe 'salir' en cualquier momento para cancelar.\n")

    # 1) Obtener todos los nombres únicos de la colección
    nombres = coll.distinct("nombre")
    if not nombres:
        print("⚠️  La colección está vacía. No hay nada para eliminar.")
        return

    # 2) Mostrar la lista de nombres al usuario
    print("Plataformas disponibles para eliminar:")
    for idx, n in enumerate(sorted(nombres), start=1):
        print(f"  [{idx}]  {n}")
    print()

    # 3) El usuario ingresa el nombre exacto (o 'salir')
    nombre_input = input("Escribe el nombre EXACTO de la plataforma que quieres eliminar (o 'salir'): ").strip()
    if nombre_input.lower() == "salir":
        print("⚠️  Eliminación cancelada por el usuario.")
        return

    if nombre_input not in nombres:
        print(f"❌  El nombre '{nombre_input}' no existe en la base de datos.")
        return

    # 4) Ya sabemos que existe: buscamos ese documento
    doc = coll.find_one({"nombre": nombre_input})
    if doc is None:
        # Aunque lo comprobamos con distinct, por si acaso:
        print("❌  Error inesperado: no se encontró el documento en la base de datos.")
        return

    _id_str = str(doc.get("_id", "<sin _id>"))
    print(f"\nDocumento encontrado:")
    print(f"  _id: {_id_str}")
    print(f"  nombre: {doc.get('nombre', '<sin nombre>')}")
    print()

    confirmar = input("¿Deseas eliminar este documento? (s/n): ").strip().lower()
    if confirmar == "s":
        eliminar_uno(coll, {"_id": doc["_id"]})
    else:
        print("⚠️  Eliminación cancelada por el usuario.")

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
