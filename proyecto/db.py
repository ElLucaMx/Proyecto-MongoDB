# db.py
from pymongo import MongoClient

def get_collection(uri: str = "mongodb://localhost:27017/", db_name: str = "consolas", coll_name: str = "plataformas"):
    client = MongoClient(uri)
    db = client[db_name]
    return db[coll_name]