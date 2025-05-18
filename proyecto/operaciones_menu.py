import re
from datetime import datetime
from bson.objectid import ObjectId
from operaciones import insertar_documento, eliminar_uno, actualizar_uno

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

    while True:
        nombre = input("Nombre de la plataforma: ").strip()
        if nombre.lower() == 'salir':
            print("Inserción cancelada.")
            return
        if not nombre:
            print("El nombre no puede estar vacío.")
            continue

        # Verificar si el nombre ya existe antes de pedir más datos
        if coll.count_documents({"nombre": nombre}) > 0:
            print(f"Ya existe una plataforma con el nombre '{nombre}'.")
            continue

        fecha_str = input("Fecha de fundación (YYYY-MM-DD): ").strip()
        if fecha_str.lower() == 'salir':
            print("Inserción cancelada.")
            return
        try:
            # Intentar parsear la fecha para validarla
            datetime.strptime(fecha_str, '%Y-%m-%d')
        except ValueError:
            print("Formato de fecha incorrecto. Usa YYYY-MM-DD.")
            continue

        valor_str = input("Valor en bolsa (número positivo): ").strip()
        if valor_str.lower() == 'salir':
            print("Inserción cancelada.")
            return
        try:
            valor = float(valor_str)
            if valor < 0:
                print("❌ El valor en bolsa debe ser un número positivo.")
                continue
        except ValueError:
            print("❌ Valor en bolsa no válido. Debe ser un número.")
            continue

        # Si todos los datos son válidos, crear el documento
        nuevo_doc = {
            "nombre": nombre,
            "fechaFundacion": fecha_str, # Guardamos como string ISO 8601 simple
            "valorEnBolsa": valor,
            "exclusivos": [], # Inicializamos el array de exclusivos vacío
            "subempresa": {} # Inicializamos el documento embebido vacío
        }

        print("\n--- Resumen del documento a insertar ---")
        print(f"Nombre: {nuevo_doc['nombre']}")
        print(f"Fecha de Fundación: {nuevo_doc['fechaFundacion']}")
        print(f"Valor en Bolsa: {nuevo_doc['valorEnBolsa']}")

        confirmacion = input("¿Confirmas la inserción? (s/n): ").strip().lower()
        if confirmacion == 's':
            insertar_documento(coll, nuevo_doc)
            break # Salir del bucle si la inserción es exitosa
        elif confirmacion == 'n':
            print("Inserción cancelada por el usuario.")
            break # Salir si el usuario cancela
        else:
            print("Respuesta no válida. Por favor, responde 's' o 'n'.")


def eliminar_menu(coll):
    """
    Pasos:
    1) Obtiene todos los nombres existentes en la colección.
    2) Muestra la lista enumerada de nombres.
    3) El usuario escribe el nombre EXACTO que quiere eliminar (o 'salir').
    4) Si no existe, muestra error y retorna.
    5) Si existe, muestra el documento encontrado (_id y nombre) y pide confirmación (s/n).
    6) Si confirma, llama a eliminar_uno(...) con el filtro correspondiente. Luego imprime resultado.
       Si no confirma, informa que se canceló y retorna.
    """
    print("\n--- ELIMINAR DOCUMENTO ---")
    print("Escribe 'salir' en cualquier momento para cancelar.\n")

    # 1) Obtiene todos los nombres existentes en la colección.
    nombres_exist = sorted([doc['nombre'] for doc in coll.find({}, {'nombre': 1})])
    if not nombres_exist:
        print("No hay documentos en la colección para eliminar.")
        return

    # 2) Muestra la lista enumerada de nombres.
    print("Nombres de plataformas existentes:")
    for idx, nombre in enumerate(nombres_exist, start=1):
        print(f"  [{idx}] {nombre}")
    print()

    # 3) El usuario escribe el nombre EXACTO que quiere eliminar (o 'salir').
    nombre_a_eliminar = input("Escribe el nombre EXACTO de la plataforma a eliminar (o 'salir'): ").strip()
    if nombre_a_eliminar.lower() == 'salir':
        print("Eliminación cancelada.")
        return

    # 4) Si no existe, muestra error y retorna.
    if nombre_a_eliminar not in nombres_exist:
        print(f"No se encontró ninguna plataforma con el nombre '{nombre_a_eliminar}'.")
        return

    # 5) Si existe, muestra el documento encontrado (_id y nombre)
    doc_encontrado = coll.find_one({"nombre": nombre_a_eliminar}, {"_id": 1, "nombre": 1})
    print("\nDocumento a eliminar:")
    print(f"  _id: {doc_encontrado['_id']}")
    print(f"  nombre: {doc_encontrado['nombre']}")

    # Pide confirmación (s/n).
    confirmacion = input("¿Confirmas la eliminación de este documento? (s/n): ").strip().lower()

    # 6) Si confirma, llama a eliminar_uno(...) con el filtro correspondiente.
    if confirmacion == 's':
        filtro = {"_id": doc_encontrado["_id"]}
        eliminar_uno(coll, filtro)
    elif confirmacion == 'n':
        print("Eliminación cancelada por el usuario.")
    else:
        print("Respuesta no válida. Eliminación cancelada.")


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

    # 1) Obtiene todos los nombres existentes en la colección.
    nombres_exist = sorted([doc['nombre'] for doc in coll.find({}, {'nombre': 1})])
    if not nombres_exist:
        print("No hay documentos en la colección para actualizar.")
        return

    # 2) Muestra la lista enumerada de nombres.
    print("Nombres de plataformas existentes:")
    for idx, nombre in enumerate(nombres_exist, start=1):
        print(f"  [{idx}] {nombre}")
    print()

    # 3) El usuario escribe el nombre EXACTO que quiere actualizar (o 'salir' para cancelar).
    nombre_a_actualizar = input("Escribe el nombre EXACTO de la plataforma a actualizar (o 'salir'): ").strip()
    if nombre_a_actualizar.lower() == 'salir':
        print("Actualización cancelada.")
        return

    # 4) Si no existe, muestra error y retorna.
    if nombre_a_actualizar not in nombres_exist:
        print(f"No se encontró ninguna plataforma con el nombre '{nombre_a_actualizar}'.")
        return

    # 5) Si existe, muestra el documento encontrado (solo _id y nombre)
    doc_encontrado = coll.find_one({"nombre": nombre_a_actualizar}, {"_id": 1, "nombre": 1})
    print("\nDocumento a actualizar:")
    print(f"  _id: {doc_encontrado['_id']}")
    print(f"  nombre: {doc_encontrado['nombre']}")

    # y pregunta qué campo actualizar:
    campo_a_actualizar = ""
    while campo_a_actualizar not in ['1', '2', '3', 'salir']:
        print("\n¿Qué campo deseas actualizar?")
        print("1) nombre")
        print("2) fechaFundacion")
        print("3) valorEnBolsa")
        print("'salir' para cancelar")
        campo_a_actualizar = input("Elige una opción [1-3] o 'salir': ").strip().lower()

        if campo_a_actualizar == 'salir':
            print("Actualización cancelada.")
            return
        if campo_a_actualizar not in ['1', '2', '3']:
            print("Opción no válida.")

    # 6) Según elección, pide el nuevo valor (validándolo en cada caso).
    nuevo_valor = None
    campo_nombre = None

    if campo_a_actualizar == '1':
        campo_nombre = 'nombre'
        while True:
            nuevo_valor = input(f"Introduce el nuevo {campo_nombre} (o 'salir'): ").strip()
            if nuevo_valor.lower() == 'salir':
                print("Actualización cancelada.")
                return
            if not nuevo_valor:
                print(f"El {campo_nombre} no puede estar vacío.")
                continue
            # Opcional: verificar si el nuevo nombre ya existe (evitar duplicados)
            if coll.count_documents({"nombre": nuevo_valor}) > 0:
                 print(f"Ya existe una plataforma con el nombre '{nuevo_valor}'.")
                 continue
            break

    elif campo_a_actualizar == '2':
        campo_nombre = 'fechaFundacion'
        while True:
            nuevo_valor_str = input(f"Introduce la nueva {campo_nombre} (YYYY-MM-DD) (o 'salir'): ").strip()
            if nuevo_valor_str.lower() == 'salir':
                print("Actualización cancelada.")
                return
            try:
                # Validar formato de fecha
                datetime.strptime(nuevo_valor_str, '%Y-%m-%d')
                nuevo_valor = nuevo_valor_str # Guardamos como string
                break
            except ValueError:
                print("Formato de fecha incorrecto. Usa YYYY-MM-DD.")

    elif campo_a_actualizar == '3':
        campo_nombre = 'valorEnBolsa'
        while True:
            nuevo_valor_str = input(f"Introduce el nuevo {campo_nombre} (número positivo) (o 'salir'): ").strip()
            if nuevo_valor_str.lower() == 'salir':
                print("Actualización cancelada.")
                return
            try:
                valor = float(nuevo_valor_str)
                if valor < 0:
                    print("El valor en bolsa debe ser un número positivo.")
                    continue
                nuevo_valor = valor
                break
            except ValueError:
                print("Valor en bolsa no válido. Debe ser un número.")

    # 7) Muestra un resumen de la actualización propuesta y pide confirmación (s/n).
    print("\n--- Actualización propuesta ---")
    print(f"Documento a actualizar (por _id): {doc_encontrado['_id']}")
    print(f"Campo a actualizar: {campo_nombre}")
    print(f"Nuevo valor: {nuevo_valor}")

    confirmacion = input("¿Confirmas esta actualización? (s/n): ").strip().lower()

    # 8) Si confirma, llama a actualizar_uno(...) con el filtro correspondiente y el operador $set.
    if confirmacion == 's':
        filtro = {"_id": doc_encontrado["_id"]}
        cambios = {"$set": {campo_nombre: nuevo_valor}}
        actualizar_uno(coll, filtro, cambios)
    elif confirmacion == 'n':
        print("Actualización cancelada por el usuario.")
    else:
        print("Respuesta no válida. Actualización cancelada.")
