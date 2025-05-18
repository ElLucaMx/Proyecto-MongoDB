from pymongo.errors import PyMongoError, DuplicateKeyError

def insertar_documento(coll, doc):
    """
    Inserta un único documento en la colección.
    Si ya existe un documento con el mismo 'nombre', alerta al usuario.
    """
    try:
        # Suponiendo que hemos puesto un índice único en 'nombre' en Mongo,
        # DuplicateKeyError saldrá si ya existe.
        resultado = coll.insert_one(doc)
        print(f"\nDocumento insertado correctamente. _id generado: {resultado.inserted_id}")
    except DuplicateKeyError:
        print("\nYa existe una plataforma con ese nombre. Inserción cancelada.")
    except PyMongoError as e:
        print(f"\nError al insertar el documento: {e}")


def eliminar_uno(coll, filtro):
    """
    Elimina un solo documento que cumpla el filtro.
    """
    try:
        res = coll.delete_one(filtro)
        if res.deleted_count == 0:
            print("No se encontró ningún documento que coincidiera con ese filtro.")
        else:
            print(f"Se eliminó 1 documento.")
    except PyMongoError as e:
        print(f"Error al eliminar documento: {e}")

def eliminar_varios(coll, filtro):
    """
    Elimina todos los documentos que cumplan el filtro.
    """
    try:
        res = coll.delete_many(filtro)
        print(f"Se eliminaron {res.deleted_count} documentos.")
    except PyMongoError as e:
        print(f"Error al eliminar documentos: {e}")

def actualizar_uno(coll, filtro, cambios):
    """
    Actualiza un único documento que cumpla el filtro.
    - coll: colección MongoDB
    - filtro: dict con las condiciones de búsqueda (p. ej. {"_id": ObjectId(...)})
    - cambios: dict con el operador de actualización (p. ej. {"$set": {"campo": nuevo_valor}})
    """
    try:
        res = coll.update_one(filtro, cambios)
        if res.matched_count == 0:
            print("️\u00a0No se encontró ningún documento que coincidiera con ese filtro.")
        elif res.modified_count == 0:
            print("️\u00a0El documento ya tenía ese valor (no se modificó nada).")
        else:
            print(f"\u00a0Se actualizó 1 documento correctamente.")
    except PyMongoError as e:
        print(f"\u00a0Error al actualizar el documento: {e}")

def actualizar_varios(coll, filtro, cambios):
    try:
        res = coll.update_many(filtro, cambios)
        print(f"{res.modified_count} documentos modificados.")
    except PyMongoError as e:
        print("Error al actualizar varios:", e)

def reemplazar_documento(coll, filtro, doc_completo):
    try:
        res = coll.replace_one(filtro, doc_completo)
        print(f"{res.modified_count} documento reemplazado.")
    except PyMongoError as e:
        print("Error al reemplazar:", e)
