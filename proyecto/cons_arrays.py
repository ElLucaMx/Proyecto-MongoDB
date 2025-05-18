# cons_arrays.py

import pprint
from pymongo import ASCENDING

def consulta_array(coll):
    """
    Sub‑menú de consultas basadas en arrays. 
    1) Juegos en “Nintendo Switch” (u otra plataforma que elija el usuario).
    2) Juegos multijugador (agrupados por plataforma).
    3) Con idioma Español (u otro idioma que elija el usuario).\n    4) Volver al menú de consultas.
    """
    opcion = ""
    while opcion != "4":
        print("\n*** CONSULTAS CON ARRAYS ***")
        print("1) Mostrar títulos de exclusivos según plataforma (p.ej. ‘Nintendo Switch’)")
        print("2) Mostrar juegos multijugador agrupados por plataforma")
        print("3) Mostrar títulos de exclusivos en un idioma dado (p.ej. ‘Español’)")
        print("4) Volver al menú")
        opcion = input("Elige una opción [1-4]: ").strip()

        if opcion == "1":
            _consulta_juegos_por_plataforma(coll)
        elif opcion == "2":
            _consulta_juegos_multijugador_por_plataforma(coll)
        elif opcion == "3":
            _consulta_juegos_por_idioma(coll)
        elif opcion == "4":
            print("Volviendo al menú de consultas.")
        else:
            print("Opción no válida. Intenta de nuevo.")

def _consulta_juegos_por_plataforma(coll):
    """
    1) Averigua todas las plataformas posibles (distinct en el array "exclusivos.jugabilidad.plataformas").
    2) Muestra la lista al usuario para que elija una.
    3) Ejecuta:
       db.plataformas.find(
         { "exclusivos.jugabilidad.plataformas": PLATAFORMA },
         { _id: 0, nombre: 1, "exclusivos.titulo": 1 }
       )
    """
    print("\n--- Juegos según plataforma ---")
    # 1) Distinct de todas las plataformas que aparecen en exclusivos.jugabilidad.plataformas
    plataformas = coll.distinct("exclusivos.jugabilidad.plataformas")
    if not plataformas:
        print("No se encontraron plataformas en los arrays de exclusivos.")
        return

    # 2) Mostrar enumerado
    plataformas_ordenadas = sorted(plataformas)
    print("Plataformas disponibles:")
    for idx, p in enumerate(plataformas_ordenadas, start=1):
        print(f"  [{idx}]  {p}")
    print()

    # 3) Pedir al usuario que escriba la plataforma EXACTA (o 'salir')
    elegido = input("Escribe el nombre EXACTO de la plataforma (o 'salir'): ").strip()
    if elegido.lower() == "salir":
        print("Consulta cancelada.")
        return

    if elegido not in plataformas_ordenadas:
        print(f"La plataforma '{elegido}' no está en la lista. Vuelve a intentarlo.")
        return

    # 4) Ejecución de la consulta
    filtro = { "exclusivos.jugabilidad.plataformas": elegido }
    proyeccion = { "_id": 0, "nombre": 1, "exclusivos.titulo": 1 }
    cursor = coll.find(filtro, proyeccion).sort("nombre", ASCENDING)
    resultados = list(cursor)
    if not resultados:
        print(f"No se encontraron juegos en la plataforma '{elegido}'.")
        return

    print(f"\nResultados: juegos en la plataforma '{elegido}':")
    for doc in resultados:
        pprint.pprint(doc)


def _consulta_juegos_multijugador_por_plataforma(coll):
    """
    1) No es necesario pedir nada al usuario (siempre se busca modo Juego = "Multijugador").
    2) Pipeline:
       - $unwind: "$exclusivos"
       - $match: { "exclusivos.jugabilidad.modoJuego": "Multijugador" }
       - $group: { _id: "$nombre", titulosMultijugador: { $push: "$exclusivos.titulo" } }
       - $project: { _id:0, plataforma: "$_id", titulosMultijugador: 1 }
    """
    print("\n--- Juegos multijugador agrupados por plataforma ---")

    pipeline = [
        { "$unwind": "$exclusivos" },
        { "$match": { "exclusivos.jugabilidad.modoJuego": "Multijugador" } },
        { "$group": {
            "_id": "$nombre",
            "titulosMultijugador": { "$push": "$exclusivos.titulo" }
        }},
        { "$project": {
            "_id": 0,
            "plataforma": "$_id",
            "titulosMultijugador": 1
        }},
        { "$sort": { "plataforma": 1 } }
    ]
    resultados = list(coll.aggregate(pipeline))
    if not resultados:
        print("No se encontraron juegos multijugador en la base de datos.")
        return

    print(f"\nResultados: plataformas con títulos multijugador")
    for doc in resultados:
        pprint.pprint(doc)


def _consulta_juegos_por_idioma(coll):
    """
    1) Averigua todos los idiomas distintos que aparecen en exclusivos.idioma.
    2) Muestra la lista al usuario para que elija un idioma.
    3) Ejecuta:
       db.plataformas.find(
         { "exclusivos.idioma": IDIOMA },
         { _id: 0, "exclusivos.titulo": 1, "exclusivos.idioma": 1 }
       )
    """
    print("\n--- Juegos según idioma ---")
    # 1) Distinct de idiomas en exclusivos.idioma
    idiomas = coll.distinct("exclusivos.idioma")
    if not idiomas:
        print("No se encontraron idiomas en los arrays de exclusivos.")
        return

    # 2) Mostrar enumerado
    idiomas_ordenados = sorted(idiomas)
    print("Idiomas disponibles:")
    for idx, i in enumerate(idiomas_ordenados, start=1):
        print(f"  [{idx}]  {i}")
    print()

    # 3) Pedir al usuario que escriba el idioma EXACTO (o 'salir')
    elegido = input("Escribe el idioma EXACTO (o 'salir'): ").strip()
    if elegido.lower() == "salir":
        print("Consulta cancelada.")
        return

    if elegido not in idiomas_ordenados:
        print(f"El idioma '{elegido}' no está en la lista. Vuelve a intentarlo.")
        return

    # 4) Ejecución de la consulta
    filtro = { "exclusivos.idioma": elegido }
    proyeccion = { "_id": 0, "exclusivos.titulo": 1, "exclusivos.idioma": 1 }
    cursor = coll.find(filtro, proyeccion).sort("exclusivos.titulo", ASCENDING)
    resultados = list(cursor)
    if not resultados:
        print(f"No se encontraron exclusivos con idioma '{elegido}'.")
        return

    print(f"\nResultados: exclusivos en idioma '{elegido}':")
    for doc in resultados:
        pprint.pprint(doc)
