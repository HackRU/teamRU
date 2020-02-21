from flask import request, jsonify
import requests
from app import app
from app.db import users, teams

base_url = "https://api.hackru.org/dev"


def call_validate_endpoint(email, token):
    data_dic = {"email": email, "token": token}
    resp = requests.post(base_url + "/validate", json=data_dic)
    resp_parsed = resp.json()
    if resp_parsed["statusCode"] == 400:
        '''{"statusCode":400,"body":"User email not found."}'''
        return resp_parsed
    if resp_parsed["statusCode"] == 403:
        '''{"statusCode": 403, "body": "Permission denied"}'''
        return resp_parsed
    if resp_parsed["statusCode"] == 200:
        return 200


def call_auth_endpoint():
    email = ""
    password = ""
    data_dic = {"email": email, "password": password}
    resp = requests.post(base_url + "/authorize", json=data_dic)
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
    resp = requests.post(base_url + "/read", json=data_dic)
    if not resp:
        return 400
    resp_parsed = resp.json()
    if resp_parsed['statusCode'] == 200:
        if not resp_parsed["body"]:
            return 400
        return resp_parsed["body"]['first_name'] + "" + resp_parsed["body"]['last_name'] + ""
    else:
        return 400


def format_string(s):
    if not s:
        return []
    elements = s.split(",")
    for i in range(0, len(elements)):
        elements[i] = elements[i].strip().lower()
    return elements


@app.route('/start-a-team', methods=['POST'])
def start_a_team(email="", token=""):
    # if call_validate_endpoint(email, token) == 200:
        if request.method == 'POST':
            data = request.get_json(silent=True)
            if not data or not 'name' in data or not 'desc' in data or not 'skills' in data:
                return {"statusCode": 400, "body": "Required info not found"}
            team_name = data['name'].strip().lower()
            team_desc = data['desc'].strip().lower()
            partner_skills = data['skills']
            formatted_skills = format_string(partner_skills)
            formatted_prizes = []
            if 'prizes' in data:
                prizes = data['prizes']
                formatted_prizes = format_string(prizes)
            team_exist = teams.find_one({"_id": str(team_name)})
            user_exists = users.find_one({"_id": email.lower()})
            if not user_exists:
                resp = jsonify({"statusCode": 403, "body": "Invalid user"})
                resp.status_code = 403
                return resp
            if team_exist:
                resp = jsonify({"statusCode": 401, "body": "Team with the same name exists"})
                resp.status_code = 401
                return resp
            else:
                user_in_a_team = users.find_one({"_id": email, "hasateam": True})
                if user_in_a_team:
                    resp = jsonify({"statusCode": 402, "body": "User in a team"})
                    resp.status_code = 402
                    return resp
                else:
                    users.update_one({"_id": email}, {"$set": {"hasateam": True}})
                teams.insert({"_id": team_name, "members": [email], "desc": team_desc, "partnerskills": formatted_skills, "prizes": formatted_prizes, "complete": False})
                resp = jsonify({"statusCode": 200, "body": "Success"})
                resp.status_code = 200
                return resp
    # else:
    #     resp = jsonify({"statusCode": 404, "body": "Invalid request"})
    #     resp.status_code = 404
    #     return resp


@app.route('/leave-team', methods=['POST'])
def leave_team(email="", token=""):
    # if call_validate_endpoint(email, token) == 200:
        if request.method == 'POST':
            user_in_a_team = users.find_one({"_id": email, "hasateam": True})
            if not user_in_a_team:
                resp = jsonify({"statusCode": 400, "body": "User doesn't have a team"})
                resp.status_code = 400
                return resp
            team_name = teams.find_one({"members": {"$all": [email]}}, {"_id"})['_id']
            team_size = len(teams.find_one({"_id": team_name})['members'])
            if team_size == 1:
                teams.delete_one({"_id": team_name})
            else:
                teams.update_one({"_id": team_name}, {"$pull": {"members": email}})
            users.update_one({"_id": email}, {"$set": {"hasateam": False}})
            teams.update_one({"_id": team_name}, {"$set": {"complete": False}})
            resp = jsonify({"statusCode": 200, "body": "Success"})
            resp.status_code = 200
            return resp
    # else:
    #     resp = jsonify({"statusCode": 404, "body": "Invalid request"})
    #     resp.status_code = 404
    #     return resp


@app.route('/add-team-member', methods=['POST'])
def add_team_member(email="", token=""):
    # if call_validate_endpoint(email, token) == 200:
        if request.method == 'POST':
            data = request.get_json(silent=True)
            if not data or 'email not in data':
                resp = jsonify({"statusCode": 400, "body": "Required info not found"})
                resp.status_code = 400
                return resp
            partner_email = data['email'].strip().lower()
            # dir_token = call_auth_endpoint()
            # if dir_token == 400:
            #     return {"statusCode": 401, "body": "auth endpoint failed"}
            # if get_name(dir_token, email) == 400:
            #     return {"statusCode": 402, "body": "read endpoint failed"}
            team_name = teams.find_one({"members": {"$all": [email]}}, {"_id"})['_id']
            team_size = len(teams.find_one({"_id": team_name})['members'])
            team_complete = teams.find_one({"_id": team_name, "complete": True})
            if team_complete or team_size >= 4:
                resp = jsonify({"statusCode": 403, "body": "Team complete"})
                resp.status_code = 403
                return resp
            user_exist = users.find_one({"_id": partner_email})
            if not user_exist:
                users.insert({"_id": partner_email, "hasateam": True, "skills": ""})
                teams.update_one({"_id": team_name}, {"$push": {"members": partner_email}})
                resp = jsonify({"statusCode": 200, "body": "Success"})
                resp.status_code = 200
                return resp
            else:
                partner_in_a_team = users.find_one({"_id": partner_email, "hasateam": True})
                if not partner_in_a_team:
                    users.update_one({"_id": partner_email}, {"$set": {"hasateam": True}})
                    teams.update_one({"_id": team_name}, {"$push": {"members": partner_email}})
                    if team_size == 4:
                        teams.update_one({"_id": team_name}, {"$set": {"complete": True}})
                    resp = jsonify({"statusCode": 200, "body": "Success"})
                    resp.status_code = 200
                    return resp
                else:
                    resp = jsonify({"statusCode": 405, "body": "User in a team"})
                    resp.status_code = 405
                    return resp
    # else:
    #     resp = jsonify({"statusCode": 404, "body": "Invalid request"})
    #     resp.status_code = 404
    #     return resp


@app.route('/team-complete', methods=['POST'])
def team_complete(email="jlf", token=""):
    # if call_validate_endpoint(email, token) == 200:
        if request.method == 'POST':
            team_name = teams.find_one({"members": {"$all": [email]}}, {"_id"})['_id']
            teams.update_one({"_id": team_name}, {"$set": {"complete": True}})
            resp = jsonify({"statusCode": 200, "body": "Success"})
            resp.status_code = 200
            return resp
    # else:
    #     resp = jsonify({"statusCode": 404, "body": "Invalid request"})
    #     resp.status_code = 404
    #     return resp


@app.route('/profile', methods=['GET', 'POST'])
def profile(email="", token=""):
    #GET is used to get a profile while POST is used to create and update a profile
    # if call_validate_endpoint(email, token) == 200:
        if request.method == 'GET':
            has_profile = users.find_one({"_id": email})
            if not has_profile:
                resp = jsonify({"statusCode": 400, "body": "User Not found"})
                resp.status_code = 200
                return resp
            user_profile = users.find_one({"_id": email})
            resp = jsonify({"statusCode": 200, "body": user_profile})
            resp.status_code = 200
            return resp
        elif request.method == 'POST':
            data = request.get_json(silent=True)
            if not data or 'skills' not in data:
                resp = jsonify({"statusCode": 400, "body": "Required info not found"})
                resp.status_code = 400
                return resp
            if 'prizes' not in data:
                prizes = []
            else:
                prizes = format_string(data['prizes'].strip().lower())
            #Enter the skills separated by a comma. example: java, flask, backend
            skills = format_string(data['skills'].strip().lower())
            user_exists = users.find_one({"_id": email})
            # update an existing profile
            if user_exists:
                # when a user updates their profile, i should get all the params again -> for frontend team
                users.update({"_id": email}, {"$set": {"skills": skills, "prizes": prizes}})
            # create a new profile
            else:
                users.insert_one({"_id": email, "skills": skills, "prizes": prizes, "hasateam": False})
            resp = jsonify({"statusCode": 200, "body": "Success"})
            resp.status_code = 200
            return resp
    # else:
    #     resp = jsonify({"statusCode": 404, "body": "Invalid request"})
    #     resp.status_code = 404
    #     return resp


@app.route('/teams', methods=['GET'])
def all_teams(email="", token=""):
    # if call_validate_endpoint(email, token) == 200:
        if request.method == 'GET':
            data = request.get_json(silent=True)
            if not data:
                open_teams = teams.find({"complete": False})
                all_open_teams = []
                for x in open_teams:
                    all_open_teams.append(x)
                if not all_open_teams:
                    resp = jsonify({"statusCode": 400, "body": "No open teams"})
                    resp.status_code = 400
                    return resp
                print("hello")
                resp = jsonify({"statusCode": 200, "body": all_open_teams})
                resp.status_code = 200
                return resp
            else:
                if 'filter' not in data:
                    resp = jsonify({"statusCode": 200, "body": "No proper json"})
                    resp.status_code = 401
                    return resp
                search = data['filter'].lower().strip()
                open_teams = teams.find({"complete": False, "$or": [
                        {"desc": {"$regex": ".*" + search + ".*"}},
                        {"skills": {"$regex": ".*" + search + ".*"}},
                        {"prizes": {"$regex": ".*" + search + ".*"}}
                             ]
                    })
                all_open_teams = []
                for x in open_teams:
                    all_open_teams.append(x)
                if not all_open_teams:
                    resp = jsonify({"statusCode": 400, "body": "No open teams"})
                    resp.status_code = 400
                    return resp
                resp = jsonify({"statusCode": 200, "body": all_open_teams})
                resp.status_code = 200
                return resp
    # else:
    #     resp = jsonify({"statusCode": 404, "body": "Invalid request"})
    #     resp.status_code = 404
    #     return resp


@app.route('/team-profile', methods=['GET'])
def team_profile(email="", token=""):
    # if call_validate_endpoint(email, token) == 200:
        if request.method == 'GET':
            team = teams.find_one({"members": {"$all": [email]}})
            if not team:
                resp = jsonify({"statusCode": 400, "body": "Team Not found"})
                resp.status_code = 400
            # team = teams.find_one({"members": {"$all": [email]}}, {"members"})
            else:
                resp = jsonify({"statusCode": 200, "body": team})
                resp.status_code = 200
            return resp
    # else:
    #     resp = jsonify({"statusCode": 404, "body": "Invalid request"})
    #     resp.status_code = 404
    #     return resp


@app.route('/team-recommendations', methods=['GET'])
def team_recommendations(email="", token=""):
    # if call_validate_endpoint(email, token) == 200:
        if request.method == 'GET':
            user = users.find_one({"_id": email})
            if not user:
                resp = jsonify({"statusCode": 403, "body": "Invalid user"})
                resp.status_code = 403
                return resp
            if 'skills' not in user:
                resp = jsonify({"statusCode": 400, "body": "No recommendations found"})
                resp.status_code = 400
                return resp
            skills = user['skills']
            names = set()
            matches = []
            for skill in skills:
                match = teams.aggregate([
                    {"$match": {"complete": False, "partnerskills": {"$all": [skill]}}}
                ])
                if not match:
                    continue
                for m in match:
                    if m['_id'] not in names:
                        names.add(m['_id'])
                        matches.append(m)
            if not matches:
                resp = jsonify({"statusCode": 400, "body": "No recommendations found"})
                resp.status_code = 400
            else:
                resp = jsonify({"statusCode": 200, "body": matches})
                resp.status_code = 200
            return resp
    # else:
    #     resp = jsonify({"statusCode": 404, "body": "Invalid request"})
    #     resp.status_code = 404
    #     return resp


@app.route('/individual-recommendations', methods=['GET'])
def individual_recommendations(email="", token=""):
    # if call_validate_endpoint(email, token) == 200:
        if request.method == 'GET':
            team = teams.find_one({"members": {"$all": [email.strip().lower()]}})
            if not team:
                resp = jsonify({"statusCode": 400, "body": "User not in a team"})
                resp.status_code = 400
                return resp
            if 'partnerskills' not in team:
                resp = jsonify({"statusCode": 401, "body": "Profile not complete"})
                resp.status_code = 401
                return resp
            skills = team['partnerskills']
            emails = set()
            matches = []
            for skill in skills:
                match = users.aggregate([
                    {"$match": {"hasateam": False, "skills": {"$all": [skill]}}}
                ])
                if not match:
                    continue
                for m in match:
                    if m['_id'] not in emails:
                        emails.add(m['_id'])
                        matches.append(m)
            if not matches:
                resp = jsonify({"statusCode": 402, "body": "No recommendations found"})
                resp.status_code = 402
            else:
                resp = jsonify({"statusCode": 200, "body": matches})
                resp.status_code = 200
            return resp
    # else:
    #     resp = jsonify({"statusCode": 404, "body": "Invalid request"})
    #     resp.status_code = 404
    #     return resp


@app.route('/interested', methods=['POST'])
def interested(email="", token=""):
    # if call_validate_endpoint(email, token) == 200:
        if request.method == 'POST':
            data = request.get_json(silent=True)
            if not data or 'name' not in data:
                resp = jsonify({"statusCode": 401, "body": "Missing inf"})
                resp.status_code = 401
                return resp
            team_name = data['name']
            team = teams.find_one({"_id": team_name})
            if not team:
                resp = jsonify({"statusCode": 402, "body": "Invalid team"})
                resp.status_code = 402
                return resp
            teams.update_one({"_id": team_name}, {"$push": {"interested": email.strip().lower()}})
    # else:
    #     resp = jsonify({"statusCode": 404, "body": "Invalid request"})
    #     resp.status_code = 404
    #     return resp


@app.route('/interested-hackers', methods=['GET'])
def interested_hackers(email="", token=""):
    # if call_validate_endpoint(email, token) == 200:
        if request.method == 'GET':
            team = teams.find_one({"members": {"$all": [email]}}, {"_id": 0, "interested": 1})
            if 'interested' not in team:
                resp = jsonify({"statusCode": 400, "body": "None"})
                resp.status_code = 400
                return resp
            interested = team['interested']
            profiles = set()
            for hacker in interested:
                profiles.add(users.find_one({"_id": hacker}))
            if not profiles:
                resp = jsonify({"statusCode": 400, "body": "None"})
                resp.status_code = 400
            else:
                resp = jsonify({"statusCode": 200, "body": profiles})
                resp.status_code = 200
            return resp
    # else:
    #     resp = jsonify({"statusCode": 404, "body": "Invalid request"})
    #     resp.status_code = 404
    #     return resp


@app.route('/confirm-member', methods=['POST'])
def confirm_member(email, token):
    # if call_validate_endpoint(email, token) == 200:
        if request.method == 'POST':
            data = request.get_json(silent=True)
            if not data or 'name' not in data:
                resp = jsonify({"statusCode": 401, "body": "Missing inf"})
                resp.status_code = 401
                return resp
            hacker = data['email'].strip().lower()
            team_name = teams.find_one({"members": {"$all": [email]}}, {"_id"})['_id']
            users.update_one({"_id": hacker}, {"$set": {"hasateam": True}})
            teams.update_one({"_id": team_name}, {"$push": {"members": hacker}})

    # else:
    #     resp = jsonify({"statusCode": 404, "body": "Invalid request"})
    #     resp.status_code = 404
    #     return resp
