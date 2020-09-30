from pymongo import MongoClient

import src.flaskapp.config as config

client = MongoClient(config.DB_URI).get_database()


def coll(coll_name):
    # coll_name can be either "users" or "teams"
    return client[coll_name]
