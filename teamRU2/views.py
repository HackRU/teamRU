from flask import Flask, render_template, request, json, make_response,jsonify,redirect,url_for
import random
from teamRU2 import app
import hashlib
import util, sql

#------------------------COOKIE LIST ------------------------------#
#                       logoff = [1,0]
#                       hash = [individual hashcode]
#                       slack = slack username

#If any authentication issues happen -> logoff cookie should be set to false
#If log off is false we can choose which routes are re-routed to home



@app.route('/', methods=['GET'])
def main():
    return render_template('home.html')


@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('home.html')
    else:
        username = request.form['user']
        password = request.form['password']
        #AUTENTICATE THE USER USING LCS
        passhash = hashlib.sha256(str(password).encode('utf-8')).hexdigest()
        select = "select * from user where user.slack = %s and user.hashCode = %s"
        result = SelectQuery(select,(username,passhash))
        if result != None:
            #Need to load up all the information to send over to dashboard to display
            response = make_response(render_template('redirects.html'))
            response.set_cookie('logoff',str(1))
            response.set_cookie('hash', passhash)
            response.set_cookie('slack',username)
            return response
        else:
            error="An HackRU account exists, but you still need to sign up for this website -> register link"
            return render_template('home.html',error=error)

@app.route('/dashboard', methods=['GET'])
def dashboard():
    logoff = request.cookies.get('logoff')
    if not logoff:
        error="Noted Logged In"
        return render_template("home.html",error=error)
    slack = request.cookies.get('slack')
    hcode = request.cookies.get('hash')
    select = "select * from user where user.slack = %s and hashCode = %s"
    result = SelectQuery(select,(slack,hcode))
    if not result:
        error="Incorrect Credentials, Please Re-login"
        return redirect(url_for('logoff'))
    #Should Query All important information
    return render_template("dashboard.html",result=result)





@app.route('/logoff',methods=['GET'])
def logoff():
    success = "Logged off Successfully"
    fail = "Error Logging Off, have you not logged in?"
    response = make_response(render_template('home.html',error=success))
    logoff = request.cookies.get('logoff')
    if not logoff or int(logoff) == 0:
        response = make_response(render_template('home.html',error=fail))
        return response
    response.set_cookie('hash','',expires=0)
    response.set_cookie('logoff','',expires=0)
    response.set_cookie('slack','',expires=0)
    return response

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        error="You are already logged in!"
        response = make_response(render_template('home.html'),error=error)
        logoff = request.cookies.get("logoff")
        if logoff or int(logoff) == 1:
            return response
        slackuser = request.form['slack']
        username = request.form['user']
        password = request.form['password']
        #AUTH Information given with LCS, Code assumes it went through without issue
        select = "select MAX(uid) as m from user"
        newUid = SelectQuery(select,())['m']
        newUid+=1
        count = 0
        while(1):
            try:
                insert = "insert into user (uid,slack,tJoined,hashCode) values(%s,%s,%s,%s)"
                newuser = {
                    "uid": newUid,
                    "slack": slackuser,
                    "tJoined":-1,
                    "hashCode": hashlib.sha256(str(password).encode('utf-8')).hexdigest()
                }
                InsertQuery(insert,(newuser['uid'],newuser['slack'],newuser['tJoined'],newuser['hashCode']))
                break
            except:
                count += 1
                if count > 100:
                    break
                newUid = SelectQuery(select,())['m']
                newUid += 1
        if count > 100:
            #Signing up the user didnt work
            error = "Sign Up Failed, Please Email sazouzi21@gmail.com"
            return render_template("register.html",error=error)
        #Need to send over data for the dashboard
        response = make_response(render_template('redirect.html'))
        response.set_cookie("logoff",str(1))
        response.set_cookie("hash",str(hashlib.sha256(str(password).encode('utf-8')).hexdigest()))
        response.set_cookie("slack",slackuser)
        return response
        



@app.route('/threadHub', methods=['GET','POST'])
def threadHub():
    if request.method == 'GET':
        select = "select threads.*, count(upvotes.*) as ct from threads, upvotes where upvotes.tid = threads.tid order by ct DESC"
        results = SelectQuery(select,(),one=False)
        #Send this through jinja to the threadhub html
        return render_template('threadHub.html',threads=results)
    elif request.method == 'POST':
        search = request.form['search']
        select = "select threads.*, count(upvotes.*) as ct from threads, upvotes where upvotes.tid = threads.tid where threads.title like '%%s%' or threads.description like '%%s%' order by ct DESC"
        results = SelectQuery(select,(search,search), one=False)
        return render_template('threadHub.html',threads=results)

@app.route('/newThread', methods=['GET','POST'])
def newThread():
    #Cookie needs to be defined on login for uid and slack
    logOff = request.cookie.get("logoff")
    if not logOff or logOff == "0":
        return render_template("threadHub.html",error="Cannot Create new Thread if not logged in!")
    slack = request.cookie.get("slack")
    hcode = request.cookie.get("hash")
    select = "select * from user where user.slack=%s and user.hashCode=%s"
    results = SelectQuery(select,())
    if not results:
        return render_template('home.html',error="Incorrect Login Credentials, please try logging in again!")
    if request.method == 'GET':
        return render_template("newTherad.html")
    elif request.method == 'POST':
        #uid already defined
        title = request.form['title']
        desc = request.form['desc']
        keywords = request.form['key']
        select = "select count(*) as ct from threads"
        value = SelectQuery(select,())['ct']
        tid = value + 1
        count = 0
        while 1:
           try:
               result = InsertQuery("Insert into threads (%s,%s,%s,%s,%s,NOW())",(tid,uid,title,desc,keywords))
               break
           except:
               tid += 1
               if count > 100:
                   break
               count += 1
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


