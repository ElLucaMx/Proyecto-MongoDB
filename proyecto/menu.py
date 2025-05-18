# menu.py

import json
from operaciones import eliminar_uno, eliminar_varios   # <-- IMPORTAR AQUÍ
from db import get_collection

def run_menu():
    coll = get_collection()

    opcion = ""
    while opcion != "5":
        print("\n=== MENÚ PRINCIPAL ===")
        print("1) Insertar documento")
        print("2) Eliminar documento")
        print("3) Actualizar documento")
        print("4) Realizar consulta")
        print("5) Salir")
        opcion = input("Elige una opción: ").strip()

        if opcion == "1":
            insertar_menu(coll)       # Ya implementado anteriormente
        elif opcion == "2":
            eliminar_menu(coll)
        elif opcion == "3":
            actualizar_menu(coll)     # (pendiente de implementación)
        elif opcion == "4":
            consultas_menu(coll)      # (pendiente de implementación)
        elif opcion == "5":
            print("– ¡Hasta luego!")
        else:
            print("❌ Opción no válida. Intenta de nuevo.")

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