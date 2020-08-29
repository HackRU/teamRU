import requests

import src.flaskapp.config as config

def call_validate_endpoint(email, token):
    payload = {"email": email, "token": token}
    resp = requests.post(f"{config.LCS_BASE_URL}/validate", json=payload)
    resp_parsed = resp.json()
    if resp_parsed["statusCode"] != 200:
        '''{"statusCode":400,"body":"User email not found."}'''
        '''{"statusCode": 403, "body": "Permission denied"}'''
        return {"message": resp_parsed["body"]}, resp_parsed["statusCode"]

    return {"message": "Successfully authenticated"}, 200

##### NOT USEFUL BELOW HERE #####

# TO BE REMOVED
def call_auth_endpoint():
    email = config.DIRECTOR_CREDENTIALS["email"]
    password = config.DIRECTOR_CREDENTIALS["password"]
    data_dic = {"email": email, "password": password}
    resp = requests.post(config.LCS_BASE_URL + "/authorize", json=data_dic)
    if not resp:
        return 400
    resp_parsed = resp.json()
    if resp_parsed['statusCode'] == 200:
        return resp_parsed['body']["auth"]["token"]
    else:
        return 400

# TO BE REMOVED
def get_name(token, email):
    dir_email = "teambuilder@hackru.org"
    data_dic = {"email": dir_email, "token": token, "query": {"email": email}}
    resp = requests.post(config.LCS_BASE_URL + "/read", json=data_dic)
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


# ONLY USED FOR TESTS
def login(email, password):
    data_dic = {"email": email, "password": password}
    resp = requests.post(config.LCS_BASE_URL + "/authorize", json=data_dic)
    if not resp:
        return 400
    resp_parsed = resp.json()
    if resp_parsed['statusCode'] == 200:
        return resp_parsed['body']["auth"]["token"]
    else:
        return 400
