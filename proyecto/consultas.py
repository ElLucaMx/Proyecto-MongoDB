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
            print("🔙 Volviendo al menú de consultas.")
        else:
            print("❌ Opción no válida. Intenta de nuevo.")


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
        print("⚠️  No se encontraron nombres de personas en los documentos embebidos.")
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
        print("⚠️ Consulta cancelada.")
        return
    if elegido not in personas_ordenadas:
        print(f"❌ El nombre '{elegido}' no está en la lista. Vuelve a intentarlo.")
        return

    # 4) Ejecutar la consulta
    filtro = { "exclusivos.desarrollo.personas.nombre": elegido }
    proyeccion = { "_id": 0, "exclusivos.$": 1 }
    cursor = coll.find(filtro, proyeccion)
    resultados = list(cursor)
    if not resultados:
        print(f"ℹ️  No se encontraron exclusivos dirigidos por '{elegido}'.")
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
        print("⚠️  No se encontraron subempresas en la colección.")
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
        print("⚠️ Consulta cancelada.")
        return
    if elegido not in subempresas_ordenadas:
        print(f"❌ La subempresa '{elegido}' no está en la lista. Vuelve a intentarlo.")
        return

    # 4) Ejecutar la consulta
    filtro = { "subempresa.nombre": elegido }
    proyeccion = { "_id": 0, "nombre": 1, "subempresa.nombre": 1 }
    cursor = coll.find(filtro, proyeccion).sort("nombre", ASCENDING)
    resultados = list(cursor)
    if not resultados:
        print(f"ℹ️  No se encontraron plataformas con subempresa '{elegido}'.")
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
        print("⚠️  No se encontraron nombres de desarrolladora en los documentos embebidos.")
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
        print("⚠️ Consulta cancelada.")
        return
    if elegido not in desarrolladoras_ordenadas:
        print(f"❌ La desarrolladora '{elegido}' no está en la lista. Vuelve a intentarlo.")
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
        print(f"ℹ️  No se encontraron exclusivos desarrollados por '{elegido}'.")
        return

    print(f"\nResultados: exclusivos desarrollados por '{elegido}':")
    for doc in resultados:
        pprint.pprint(doc)

def consulta_agrupacion(coll):
    """
    Sub‑menú de consultas de agregación.
    1) Ventas totales por plataforma (top 3)
    2) Volver al menú de consultas
    """
    opcion = ""
    while opcion != "2":
        print("\n*** CONSULTA DE AGRUPACIÓN ***")
        print("1) Ventas totales por plataforma (top 3)")
        print("2) Volver al menú de consultas")
        opcion = input("Elige una opción [1-2]: ").strip()

        if opcion == "1":
            _ventas_totales_top3(coll)
        elif opcion == "2":
            print("🔙 Volviendo al menú de consultas.")
        else:
            print("❌ Opción no válida. Intenta de nuevo.")

def _ventas_totales_top3(coll):
    """
    1) Despliega los 3 primeros documentos resultado de:
       db.plataformas.aggregate([
         { $unwind: "$exclusivos" },
         { $group: {
             _id: "$nombre",
             ventasTotales: { $sum: "$exclusivos.finanzas.ventas" }
           }
         },
         { $sort: { ventasTotales: -1 } },
         { $limit: 3 }
       ]);
    2) Muestra _id (plataforma) y ventasTotales.
    """
    print("\n--- Ventas totales por plataforma (TOP 3) ---")
    pipeline = [
        { "$unwind": "$exclusivos" },
        { "$group": {
            "_id": "$nombre",
            "ventasTotales": { "$sum": "$exclusivos.finanzas.ventas" }
        }},
        { "$sort": { "ventasTotales": -1 } },
        { "$limit": 3 }
    ]
    resultados = list(coll.aggregate(pipeline))
    if not resultados:
        print("ℹ️ No se obtuvieron resultados de agregación (quizá no haya datos).")
        return

    for doc in resultados:
        # doc["_id"] es el nombre de la plataforma
        pprint.pprint({
            "plataforma": doc["_id"],
            "ventasTotales": doc["ventasTotales"]
        })