# consultas.py
import pprint
from pymongo import ASCENDING, DESCENDING

def consulta_simple(coll):
    # Ejemplo: buscar todas las consolas con valorEnBolsa > X
    x = float(input("Introduce valor mínimo en bolsa: "))
    cursor = coll.find({"valorEnBolsa": {"$gt": x}},
                        {"_id": 0, "nombre": 1, "valorEnBolsa": 1}) \
                 .sort("valorEnBolsa", DESCENDING).limit(10)
    for doc in cursor:
        pprint.pprint(doc)

def consulta_array(coll):
    # Ejemplo: buscar juegos cuyo array de 'idioma' incluya 'Español'
    idioma = input("Introduce idioma a buscar (por ej. Español): ")
    cursor = coll.find({"exclusivos.idioma": idioma},
                        {"_id": 0, "nombre": 1, "exclusivos.$": 1})
    for doc in cursor:
        pprint.pprint(doc)

def consulta_embebido(coll):
    # Ejemplo: buscar juegos donde alguna persona en desarrollo tenga rol 'Director'
    cursor = coll.find({"exclusivos.desarrollo.personas.rol": "Director"},
                        {"_id": 0, "nombre": 1, "exclusivos.$": 1})
    for doc in cursor:
        pprint.pprint(doc)

def consulta_agrupacion(coll):
    # Ejemplo: agrupar por plataforma (array) y contar cuántos exclusivos hay
    pipeline = [
        {"$unwind": "$exclusivos"},
        {"$unwind": "$exclusivos.jugabilidad.plataformas"},
        {"$group": {
            "_id": "$exclusivos.jugabilidad.plataformas",
            "total_juegos": {"$sum": 1}
        }},
        {"$sort": {"total_juegos": -1}}
    ]
    resultados = coll.aggregate(pipeline)
    for r in resultados:
        pprint.pprint(r)
