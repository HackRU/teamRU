from pymongo import MongoClient

client = MongoClient("mongodb://m001-student:amany@cluster0-shard-00-00-vdddk.mongodb.net:27017,cluster0-shard-00-01-vdddk.mongodb.net:27017,cluster0-shard-00-02-vdddk.mongodb.net:27017/hackru?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true&w=majority")
db = client['hackru']
users = db['users']
teams = db['teams']
threads = db['threads']

