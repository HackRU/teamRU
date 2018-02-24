from flask import Flask, render_template, request, json
import random
from teamRU import app

@app.route('/', methods=['GET'])
def main():
    return render_template('home.html')




@app.route('/threadHub', methods=['GET','POST'])
def threadHub():
    if request.method == 'GET':
        select = "select threads.*, count(upvotes.*) as ct from threads, upvotes where upvotes.tid = threads.tid order by ct DESC"
        results = SelectQuery(select,(),one=False)
        #Send this through jinja to the threadhub html
        return render_template('home.html')
    elif request.method == 'POST':
        search = request.form['search']



