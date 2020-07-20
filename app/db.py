from pymongo import MongoClient
import app.config as config


def get_db():
    return MongoClient(config.DB_URI).get_database()


def coll(coll_name):
    return get_db()[config.DB_COLLECTIONS[coll_name]]
