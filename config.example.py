from pymongo import MongoClient

client = MongoClient("URI CONNECTION STRING")
db = client['databasename']
users = db['usersCollection']
teams = db['teamsCollection']