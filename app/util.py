from flask import jsonify
import requests
import app.config as config
from pymongo import MongoClient


def get_db():
    return MongoClient(config.DB_URI).get_database()


def coll(coll_name):
    return get_db()[config.DB_COLLECTIONS[coll_name]]


def call_validate_endpoint(email, token):
    data_dic = {"email": email, "token": token}
    resp = requests.post(config.BASE_URL + "/validate", json=data_dic)
    resp_parsed = resp.json()
    if resp_parsed["statusCode"] == 400:
        '''{"statusCode":400,"body":"User email not found."}'''
        return resp_parsed
    if resp_parsed["statusCode"] == 403:
        '''{"statusCode": 403, "body": "Permission denied"}'''
        return resp_parsed
    if resp_parsed["statusCode"] == 200:
        return 200


def login(email, password):
    data_dic = {"email": email, "password": password}
    resp = requests.post(config.BASE_URL + "/authorize", json=data_dic)
    if not resp:
        return 400
    resp_parsed = resp.json()
    if resp_parsed['statusCode'] == 200:
        return resp_parsed['body']["auth"]["token"]
    else:
        return 400


def call_auth_endpoint():
    email = config.DIRECTOR_CREDENTIALS["email"]
    password = config.DIRECTOR_CREDENTIALS["password"]
    data_dic = {"email": email, "password": password}
    resp = requests.post(config.BASE_URL + "/authorize", json=data_dic)
    if not resp:
        return 400
    resp_parsed = resp.json()
    if resp_parsed['statusCode'] == 200:
        return resp_parsed['body']["auth"]["token"]
    else:
        return 400


def get_name(token, email):
    dir_email = "teambuilder@hackru.org"
    data_dic = {"email": dir_email, "token": token, "query": {"email": email}}
    resp = requests.post(config.BASE_URL + "/read", json=data_dic)
    if not resp:
        return 400
    resp_parsed = resp.json()
    if resp_parsed['statusCode'] == 200:
        if not resp_parsed["body"]:
            return 400
        name = ""
        if 'first_name' in resp_parsed["body"][0]:
            name = name + resp_parsed["body"][0]['first_name']
        if 'last_name' in resp_parsed["body"][0]:
            name = name + " " + resp_parsed["body"][0]['last_name']
        return name
    else:
        return 400


def format_string(s):
    if not s:
        return []
    elements = s.split(",")
    for i in range(0, len(elements)):
        elements[i] = elements[i].strip().lower()
    return elements


def return_resp(code, body):
    resp = jsonify({"statusCode": code, "body": body})
    resp.status_code = code
    return resp