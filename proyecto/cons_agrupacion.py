import pprint

def consulta_agrupacion(coll):
    """
    Sub‑menú de consultas de agregación.
    1) Ventas totales por plataforma (top 3)
    2) Volver al menú de consultas
    """
    opcion = ""
    while opcion != "2":
        print("\n*** CONSULTA DE AGRUPACIÓN ***")
        print("1) Ventas totales por plataforma (top\u00a03)")
        print("2) Volver al menú")
        opcion = input("Elige una opción [1-2]: ").strip()

        if opcion == "1":
            _ventas_totales_top3(coll)
        elif opcion == "2":
            print("Volviendo al menú de consultas.")
        else:
            print("Opción no válida. Intenta de nuevo.")

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
    print("\n--- Ventas totales por plataforma (TOP\u00a03) ---")
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
