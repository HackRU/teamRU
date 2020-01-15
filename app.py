from pymongo import MongoClient
from flask import Flask, render_template, request, json, make_response, jsonify, redirect, url_for

app = Flask(__name__)

client = MongoClient('mongodb://m001-student:m001-mongodb-basics@cluster0-shard-00-00-vdddk.mongodb.net:27017,cluster0-shard-00-01-vdddk.mongodb.net:27017,cluster0-shard-00-02-vdddk.mongodb.net:27017/test?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true&w=majority')
db = client['hackru']


@app.route('/all-threads', methods=['GET', 'POST'])
def all_threads():
    # GET will be used to display all the threads while POST will be used to search for specific threads
    if request.method == 'GET':
        result = list(db.all_threads.find().sort([("votes", -1)]))
        # return all threads in descending order
        return render_template('all_threads.html', threads=result)

    elif request.method == 'POST':
        search = request.form['search']
        result = list(
            db.all_threads.find({
                "$or": [
                    {"Description": {"$regex": ".*"+search+".*"}},
                    {"Title": {"$regex": ".*"+search+".*"}}
                    ]
                })
            )
        # return all threads that have specific words in the title or description
        return render_template('all_threads.html', threads=result)


if __name__ == '__main__':
    app.run()
