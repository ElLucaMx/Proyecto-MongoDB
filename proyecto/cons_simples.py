# cons_simples.py

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
            print("Volviendo al menú.")
        else:
            print("Opción no válida. Intenta de nuevo.")


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
        print("No hay plataformas en la base de datos.")
        return

    print(f"\nTotal encontradas: {len(resultados)}")
    for doc in resultados:
        pprint.pprint(doc)


def _consulta_fundadas_antes_1950(coll):
    """
    2) Plataformas fundadas antes de 1950: mostrar { nombre, fechaFundacion }, limit 5.
    (Asumimos que 'fechaFundacion' es cadena ISO; comparamos con '1950-01-01T00:00:00Z'.)
    """
    print("\n--- Plataformas fundadas antes de 1950 (limit\u00a05) ---")
    filtro = { "fechaFundacion": { "$lt": "1950-01-01T00:00:00Z" } }
    proyeccion = { "_id": 0, "nombre": 1, "fechaFundacion": 1 }
    cursor = coll.find(filtro, proyeccion).limit(5)
    resultados = list(cursor)
    if not resultados:
        print("️\u00a0No se encontraron plataformas fundadas antes de 1950.")
        return

    for doc in resultados:
        pprint.pprint(doc)


def _consulta_juegos_punt95(coll):
    """
    3) Juegos (exclusivos) con puntuación >= 95:
       pipeline: unwind exclusivos, match exclusivos.puntuacionCritica >= 95,
                 project exclusivos.titulo y exclusivos.puntuacionCritica, sort desc.
    """
    print("\n--- Juegos con puntuación \u2265\u00a095 ---")
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
        print("ℹ️\u00a0No hay juegos con puntuación \u2265\u00a095.")
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
        print("️\u00a0No se encontraron plataformas con subempresa.")
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
        print("️\u00a0Consulta cancelada.")
        return
    if len(letra) != 1 or not letra.isalpha():
        print("\u00a0Debes introducir exactamente una letra (A-Z).")
        return

    # Construimos regex ^Letra ignorando mayúsculas/minúsculas
    regex = f"^{letra}"
    filtro = { "nombre": { "$regex": regex, "$options": "i" } }
    proyeccion = { "_id": 0, "nombre": 1 }
    cursor = coll.find(filtro, proyeccion).sort("nombre", ASCENDING)
    resultados = list(cursor)
    if not resultados:
        print(f"️\u00a0No se encontraron plataformas cuyo nombre empiece por '{letra.upper()}'.")
        return

    for doc in resultados:
        pprint.pprint(doc)
