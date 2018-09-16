import csv
import pymysql
from teamru import config.example.py
import datetime
import sys
def connect():
    connect = pymysql.connect(host = config.host, user = config.username, password = config.password, db = "teamru", cursorclass = pymysql.cursors.DictCursor)
    return connect

def InsertQuery(query:str, x):
    ret = 0
    con = connect()
    try:
        with con.cursor() as cursor:
            cursor.execute(query,x)
            ret = 1
    except:
        con.close()
        return ret
    con.commit()
    con.close()
    return ret
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

