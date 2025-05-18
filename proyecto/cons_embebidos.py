import pprint
from pymongo import ASCENDING

def consulta_embebido(coll):
    """
    Sub‑menú de consultas basadas en campos embebidos.
    1) Dirigidos por <persona>     → busca exclusivo donde exclusivos.desarrollo.personas.nombre = persona
    2) Subempresa “<subempresa>”   → busca plataforma donde subempresa.nombre = subempresa
    3) Desarrolladora “<desarrolladora>”
       → busca exclusivos donde exclusivos.desarrollo.desarrolladora = desarrolladora
    4) Volver al menú de consultas
    """
    opcion = ""
    while opcion != "4":
        print("\n*** CONSULTAS CON DOCUMENTOS EMBEBIDOS ***")
        print("1) Mostrar exclusivos dirigidos por alguien concreto")
        print("2) Mostrar plataformas que pertenezcan a subempresa concreta")
        print("3) Mostrar exclusivos de una desarrolladora concreta")
        print("4) Volver al menú de consultas")
        opcion = input("Elige una opción [1-4]: ").strip()

        if opcion == "1":
            _consulta_por_persona(coll)
        elif opcion == "2":
            _consulta_subempresa(coll)
        elif opcion == "3":
            _consulta_por_desarrolladora(coll)
        elif opcion == "4":
            print("Volviendo al menú de consultas.")
        else:
            print("Opción no válida. Intenta de nuevo.")

def _consulta_por_persona(coll):
    """
    1) Obtiene todos los nombres de 'exclusivos.desarrollo.personas.nombre' (distinct).
    2) Muestra la lista para que el usuario elija uno.
    3) Ejecuta:
       db.plataformas.find(
         { "exclusivos.desarrollo.personas.nombre": PERSONA },
         { _id: 0, "exclusivos.$": 1 }
       )
    """
    print("\n--- Buscar exclusivos dirigidos por X ---")
    # 1) Obtener distinct de nombres de persona
    personas = coll.distinct("exclusivos.desarrollo.personas.nombre")
    if not personas:
        print("No se encontraron nombres de personas en los documentos embebidos.")
        return

    # 2) Mostrar la lista ordenada
    personas_ordenadas = sorted(personas)
    print("Lista de personas (directores) encontrados en 'exclusivos.desarrollo.personas.nombre':")
    for idx, p in enumerate(personas_ordenadas, start=1):
        print(f"  [{idx}]  {p}")
    print()

    # 3) Pedir al usuario que elija una persona (o 'salir')
    elegido = input("Escribe el nombre EXACTO de la persona (o 'salir'): ").strip()
    if elegido.lower() == "salir":
        print("Consulta cancelada.")
        return
    if elegido not in personas_ordenadas:
        print(f"El nombre '{elegido}' no está en la lista. Vuelve a intentarlo.")
        return

    # 4) Ejecutar la consulta
    filtro = { "exclusivos.desarrollo.personas.nombre": elegido }
    proyeccion = { "_id": 0, "exclusivos.$": 1 }
    cursor = coll.find(filtro, proyeccion)
    resultados = list(cursor)
    if not resultados:
        print(f"No se encontraron exclusivos dirigidos por '{elegido}'.")
        return

    print(f"\nResultados: exclusivos dirigidos por '{elegido}':")
    for doc in resultados:
        pprint.pprint(doc)

def _consulta_subempresa(coll):
    """
    1) Obtiene todos los valores de 'subempresa.nombre' (distinct).
    2) Muestra la lista para que el usuario elija uno.
    3) Ejecuta:
       db.plataformas.find(
         { "subempresa.nombre": SUBEMPRESA },
         { _id: 0, nombre: 1, "subempresa.nombre": 1 }
       )
    """
    print("\n--- Plataformas según subempresa concreta ---")
    # 1) Distinct de subempresa.nombre
    subempresas = coll.distinct("subempresa.nombre")
    if not subempresas:
        print("No se encontraron subempresas en la colección.")
        return

    # 2) Mostrar la lista ordenada
    subempresas_ordenadas = sorted(subempresas)
    print("Lista de subempresas encontradas en 'subempresa.nombre':")
    for idx, s in enumerate(subempresas_ordenadas, start=1):
        print(f"  [{idx}]  {s}")
    print()

    # 3) Pedir al usuario que elija una subempresa (o 'salir')
    elegido = input("Escribe el nombre EXACTO de la subempresa (o 'salir'): ").strip()
    if elegido.lower() == "salir":
        print("Consulta cancelada.")
        return
    if elegido not in subempresas_ordenadas:
        print(f"La subempresa '{elegido}' no está en la lista. Vuelve a intentarlo.")
        return

    # 4) Ejecutar la consulta
    filtro = { "subempresa.nombre": elegido }
    proyeccion = { "_id": 0, "nombre": 1, "subempresa.nombre": 1 }
    cursor = coll.find(filtro, proyeccion).sort("nombre", ASCENDING)
    resultados = list(cursor)
    if not resultados:
        print(f"No se encontraron plataformas con subempresa '{elegido}'.")
        return

    print(f"\nResultados: plataformas con subempresa '{elegido}':")
    for doc in resultados:
        pprint.pprint(doc)

def _consulta_por_desarrolladora(coll):
    """
    1) Obtiene todos los valores de 'exclusivos.desarrollo.desarrolladora' (distinct).
    2) Muestra la lista para que el usuario elija una.
    3) Ejecuta:
       db.plataformas.find(
         { "exclusivos.desarrollo.desarrolladora": DESARROLLADORA },
         {
           _id: 0,
           exclusivos: {
             $elemMatch: { "desarrollo.desarrolladora": DESARROLLADORA }
           }
         }
       )
    """
    print("\n--- Buscar exclusivos por desarrolladora ---")
    # 1) Distinct de desarrolladoras
    desarrolladoras = coll.distinct("exclusivos.desarrollo.desarrolladora")
    if not desarrolladoras:
        print("No se encontraron nombres de desarrolladora en los documentos embebidos.")
        return

    # 2) Mostrar la lista ordenada
    desarrolladoras_ordenadas = sorted(desarrolladoras)
    print("Lista de desarrolladoras encontradas en 'exclusivos.desarrollo.desarrolladora':")
    for idx, d in enumerate(desarrolladoras_ordenadas, start=1):
        print(f"  [{idx}]  {d}")
    print()

    # 3) Pedir al usuario que elija una desarrolladora (o 'salir')
    elegido = input("Escribe el nombre EXACTO de la desarrolladora (o 'salir'): ").strip()
    if elegido.lower() == "salir":
        print("Consulta cancelada.")
        return
    if elegido not in desarrolladoras_ordenadas:
        print(f"La desarrolladora '{elegido}' no está en la lista. Vuelve a intentarlo.")
        return

    # 4) Ejecutar la consulta con $elemMatch
    filtro = { "exclusivos.desarrollo.desarrolladora": elegido }
    proyeccion = {
        "_id": 0,
        "exclusivos": {
            "$elemMatch": { "desarrollo.desarrolladora": elegido }
        }
    }
    cursor = coll.find(filtro, proyeccion)
    resultados = list(cursor)
    if not resultados:
        print(f"No se encontraron exclusivos desarrollados por '{elegido}'.")
        return

    print(f"\nResultados: exclusivos desarrollados por '{elegido}':")
    for doc in resultados:
        pprint.pprint(doc)