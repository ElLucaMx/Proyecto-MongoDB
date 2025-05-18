# operaciones.py

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
        print(f"\n✅ Documento insertado correctamente. _id generado: {resultado.inserted_id}")
    except DuplicateKeyError:
        print("\n❌ Ya existe una plataforma con ese nombre. Inserción cancelada.")
    except PyMongoError as e:
        print(f"\n❌ Error al insertar el documento: {e}")


def insertar_varios(coll, lista_docs):
    try:
        resultado = coll.insert_many(lista_docs)
        print(f"{len(resultado.inserted_ids)} documentos insertados.")
    except PyMongoError as e:
        print("Error al insertar varios documentos:", e)

def eliminar_uno(coll, filtro):
    try:
        res = coll.delete_one(filtro)
        print(f"{res.deleted_count} documento eliminado.")
    except PyMongoError as e:
        print("Error al eliminar:", e)

def eliminar_varios(coll, filtro):
    try:
        res = coll.delete_many(filtro)
        print(f"{res.deleted_count} documentos eliminados.")
    except PyMongoError as e:
        print("Error al eliminar varios:", e)

def actualizar_uno(coll, filtro, cambios):
    try:
        res = coll.update_one(filtro, cambios)
        print(f"{res.modified_count} documento modificado.")
    except PyMongoError as e:
        print("Error al actualizar:", e)

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