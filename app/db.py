from pymongo import MongoClient
client = MongoClient()
db = client['hackru']
users = db['users']
teams = db['teams']
