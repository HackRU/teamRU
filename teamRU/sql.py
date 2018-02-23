import csv
import pymysql
import config
import datetime
import sys
from abrev import abrev 
def connect():
    connect = pymysql.connect(host = config.host, user = config.username, password = config.password, db = "DS", cursorclass = pymysql.cursors.DictCursor)
    return connect

def InsertQuery(query:str, x):
    con = connect()
    with con.cursor() as cursor:
        cursor.execute(query,x)
    con.commit()
    con.close()
def SelectQuery(query:str, x = None, one:bool = True)->dict:
    con = connect()
    with con.cursor() as cursor:
        cursor.execute(query,x)
        return cursor.fetchone() if one else cursor.fetchall()
    con.close()

def stateSwp(abr:str):
    for x in abrev:
        if x[1].replace(" ","").upper().replace("'","") == abr.replace(" ","").upper().replace("'",""):
            return x[0]
    return None

