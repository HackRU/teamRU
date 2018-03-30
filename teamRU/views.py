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
        select = "select threads.*, count(upvotes.*) as ct from threads, upvotes where upvotes.tid = threads.tid where threads.title like '%%s%' or threads.description like '%%s%' order by ct DESC"
        results = SelectQuery(select,(search,search), one=False)
        return render_template('home.html')

@app.route('/newThread', methods=['GET','POST'])
def newThread():
    #Cookie needs to be defined on login for uid and slack
    if not authenticate(uid,slack):
        render_template('home.html')
    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        #uid already defined
        title = request.form['title']
        desc = request.form['desc']
        keywords = request.form['key']
        select = "select count(*) as ct from threads"
        value = SelectQuery(select,())['ct']
        tid = value + 1
        result = 0
        while result == 0:
           result = InsertQuery("Insert into threads (%s,%s,%s,%s,%s,NOW())",(tid,uid,title,desc,keywords))
           tid += 1
        #Insert Complete: Render the threads page
        return render_template('threadHub')


@app.route('/thread',methods=['GET','POST'])
def thread():
    #GET will be used to display the contents of the thread while POST will be used for comment/upvotes/joins
    if request.method == 'GET':
        #Grab tid of what was clicked through some previous button
        tid = False
        select = 'select * from threads where threads.tid = %s'
        results = SelectQuery(select,(tid))
        select = 'select * from comments where comments.tid = %s'
        comments = SelectQuery(select,(tid))
        results['comments'] = comments
        select = 'select count(*) from upvotes where upvotes.tid = %s'
        upvotes = SelectQuery(select,(tid))
        results['up'] = upvotes
        #DO JOINED LOGIC AS WELL
        if results == None:
            return render_template(threadHub)
        else:
            #NEED TO RETURN RESULT TO THIS TEMPLATE!
            return render_template('thread')
    elif request.method == 'POST':
        #See if upvote button was pressed and if comment section was changed
        upvote = 1
        comment = "some random comment"
        if upvote:
            result = InsertQuery()


