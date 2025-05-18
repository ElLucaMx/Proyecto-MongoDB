# consultas.py

import pprint
from datetime import datetime
from pymongo import ASCENDING, DESCENDING

def consulta_simple_menu(coll):
    """
    Mini‑menú con las cinco consultas simples predefinidas:
    1) Listar todas las plataformas (nombre y valorEnBolsa, ordenadas desc).
    2) Plataformas fundadas antes de 1950 (limit 5).
    3) Juegos con puntuación >= 95 (unwind + match).
    4) Plataformas con subempresa.
    5) Nombres que empiecen por letra X (letra pedida al usuario).
    6) Volver al menú de consultas.
    """

    opcion = ""
    while opcion != "6":
        print("\n*** CONSULTAS SIMPLES PREDEFINIDAS ***")
        print("1) Listar todas las plataformas (nombre, valorEnBolsa) ordenadas desc.")
        print("2) Plataformas fundadas antes de 1950 (mostrar nombre y fechaFundacion, limit 5)")
        print("3) Mostrar todos los juegos con puntuación ≥ 95")
        print("4) Listar plataformas que tengan subempresa (mostrar nombre y subempresa.nombre)")
        print("5) Listar nombres que empiecen por una letra X (se pedirá la letra)")
        print("6) Volver al menú de consultas")
        opcion = input("Elige una opción [1-6]: ").strip()

        if opcion == "1":
            _consulta_todas_plataformas(coll)
        elif opcion == "2":
            _consulta_fundadas_antes_1950(coll)
        elif opcion == "3":
            _consulta_juegos_punt95(coll)
        elif opcion == "4":
            _consulta_con_subempresa(coll)
        elif opcion == "5":
            _consulta_nombres_por_letra(coll)
        elif opcion == "6":
            print("🔙 Volviendo al menú de consultas.")
        else:
            print("❌ Opción no válida. Intenta de nuevo.")


def _consulta_todas_plataformas(coll):
    """
    1) Listar todas las plataformas: mostrar { nombre, valorEnBolsa }, ordenadas valorEnBolsa desc.
    """
    print("\n--- Listar todas las plataformas (nombre, valorEnBolsa) ordenadas desc ---")
    cursor = (
        coll
        .find({}, {"_id": 0, "nombre": 1, "valorEnBolsa": 1})
        .sort("valorEnBolsa", DESCENDING)
    )
    resultados = list(cursor)
    if not resultados:
        print("ℹ️ No hay plataformas en la base de datos.")
        return

    print(f"\nTotal encontradas: {len(resultados)}")
    for doc in resultados:
        pprint.pprint(doc)


def _consulta_fundadas_antes_1950(coll):
    """
    2) Plataformas fundadas antes de 1950: mostrar { nombre, fechaFundacion }, limit 5.
    (Asumimos que 'fechaFundacion' es cadena ISO; comparamos con '1950-01-01T00:00:00Z'.)
    """
    print("\n--- Plataformas fundadas antes de 1950 (limit 5) ---")
    filtro = { "fechaFundacion": { "$lt": "1950-01-01T00:00:00Z" } }
    proyeccion = { "_id": 0, "nombre": 1, "fechaFundacion": 1 }
    cursor = coll.find(filtro, proyeccion).limit(5)
    resultados = list(cursor)
    if not resultados:
        print("ℹ️ No se encontraron plataformas fundadas antes de 1950.")
        return

    for doc in resultados:
        pprint.pprint(doc)


def _consulta_juegos_punt95(coll):
    """
    3) Juegos (exclusivos) con puntuación >= 95:
       pipeline: unwind exclusivos, match exclusivos.puntuacionCritica >= 95,
                 project exclusivos.titulo y exclusivos.puntuacionCritica, sort desc.
    """
    print("\n--- Juegos con puntuación ≥ 95 ---")
    pipeline = [
        { "$unwind": "$exclusivos" },
        { "$match": { "exclusivos.puntuacionCritica": { "$gte": 95 } } },
        { "$project": {
            "_id": 0,
            "exclusivos.titulo": 1,
            "exclusivos.puntuacionCritica": 1
        }},
        { "$sort": { "exclusivos.puntuacionCritica": -1 } }
    ]
    resultados = list(coll.aggregate(pipeline))
    if not resultados:
        print("ℹ️ No hay juegos con puntuación ≥ 95.")
        return

    for doc in resultados:
        pprint.pprint(doc)


def _consulta_con_subempresa(coll):
    """
    4) Plataformas que tengan subempresa: mostrar { nombre, subempresa.nombre }.
    """
    print("\n--- Plataformas con subempresa ---")
    filtro = { "subempresa.nombre": { "$exists": True } }
    proyeccion = { "_id": 0, "nombre": 1, "subempresa.nombre": 1 }
    cursor = coll.find(filtro, proyeccion)
    resultados = list(cursor)
    if not resultados:
        print("ℹ️ No se encontraron plataformas con subempresa.")
        return

    for doc in resultados:
        pprint.pprint(doc)


def _consulta_nombres_por_letra(coll):
    """
    5) Pedir al usuario una letra inicial; listar plataformas cuyo 'nombre' empiece por esa letra.
    """
    print("\n--- Nombres que empiecen por letra X ---")
    letra = input("Introduce la letra inicial (A-Z) o 'salir' para cancelar: ").strip()
    if letra.lower() == "salir":
        print("⚠️ Consulta cancelada.")
        return
    if len(letra) != 1 or not letra.isalpha():
        print("❌ Debes introducir exactamente una letra (A-Z).")
        return

    # Construimos regex ^Letra ignorando mayúsculas/minúsculas
    regex = f"^{letra}"
    filtro = { "nombre": { "$regex": regex, "$options": "i" } }
    proyeccion = { "_id": 0, "nombre": 1 }
    cursor = coll.find(filtro, proyeccion).sort("nombre", ASCENDING)
    resultados = list(cursor)
    if not resultados:
        print(f"ℹ️ No se encontraron plataformas cuyo nombre empiece por '{letra.upper()}'.")
        return

    for doc in resultados:
        pprint.pprint(doc)



def consulta_array(coll):
    """
    Sub‑menú de consultas basadas en arrays. 
    1) Juegos en “Nintendo Switch” (u otra plataforma que elija el usuario).
    2) Juegos multijugador (agrupados por plataforma).
    3) Con idioma Español (u otro idioma que elija el usuario).
    4) Volver al menú de consultas.
    """
    opcion = ""
    while opcion != "4":
        print("\n*** CONSULTAS CON ARRAYS ***")
        print("1) Mostrar títulos de exclusivos según plataforma (p.ej. ‘Nintendo Switch’)")
        print("2) Mostrar juegos multijugador agrupados por plataforma")
        print("3) Mostrar títulos de exclusivos en un idioma dado (p.ej. ‘Español’)")
        print("4) Volver al menú de consultas")
        opcion = input("Elige una opción [1-4]: ").strip()

        if opcion == "1":
            _consulta_juegos_por_plataforma(coll)
        elif opcion == "2":
            _consulta_juegos_multijugador_por_plataforma(coll)
        elif opcion == "3":
            _consulta_juegos_por_idioma(coll)
        elif opcion == "4":
            print("🔙 Volviendo al menú de consultas.")
        else:
            print("❌ Opción no válida. Intenta de nuevo.")

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
        print("⚠️ No se encontraron plataformas en los arrays de exclusivos.")
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
        print("⚠️ Consulta cancelada.")
        return

    if elegido not in plataformas_ordenadas:
        print(f"❌ La plataforma '{elegido}' no está en la lista. Vuelve a intentarlo.")
        return

    # 4) Ejecución de la consulta
    filtro = { "exclusivos.jugabilidad.plataformas": elegido }
    proyeccion = { "_id": 0, "nombre": 1, "exclusivos.titulo": 1 }
    cursor = coll.find(filtro, proyeccion).sort("nombre", ASCENDING)
    resultados = list(cursor)
    if not resultados:
        print(f"ℹ️ No se encontraron juegos en la plataforma '{elegido}'.")
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
        print("ℹ️ No se encontraron juegos multijugador en la base de datos.")
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
        print("⚠️ No se encontraron idiomas en los arrays de exclusivos.")
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
        print("⚠️ Consulta cancelada.")
        return

    if elegido not in idiomas_ordenados:
        print(f"❌ El idioma '{elegido}' no está en la lista. Vuelve a intentarlo.")
        return

    # 4) Ejecución de la consulta
    filtro = { "exclusivos.idioma": elegido }
    proyeccion = { "_id": 0, "exclusivos.titulo": 1, "exclusivos.idioma": 1 }
    cursor = coll.find(filtro, proyeccion).sort("exclusivos.titulo", ASCENDING)
    resultados = list(cursor)
    if not resultados:
        print(f"ℹ️ No se encontraron exclusivos con idioma '{elegido}'.")
        return

    print(f"\nResultados: exclusivos en idioma '{elegido}':")
    for doc in resultados:
        pprint.pprint(doc)

def consulta_embebido(coll):
    """
    (Aquí pondrías tu consulta con documentos embebidos. Por ahora un placeholder.)
    """
    print("\n--- CONSULTA CON DOCUMENTOS EMBEBIDOS (pendiente) ---")
    print("Esta sección está pendiente de implementación.")


def consulta_agrupacion(coll):
    """
    (Aquí pondrías tu consulta de agregación. Por ahora un placeholder.)
    """
    print("\n--- CONSULTA DE AGRUPACIÓN (pendiente) ---")
    print("Esta sección está pendiente de implementación.")
