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


def login(email, password):
    data_dic = {"email": email, "password": password}
    resp = requests.post(base_url + "/authorize", json=data_dic)
    if not resp:
        return 400
    resp_parsed = resp.json()
    if resp_parsed['statusCode'] == 200:
        return resp_parsed['body']["auth"]["token"]
    else:
        return 400


def call_auth_endpoint():
    email = "teambuilder@hackru.org"
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


@app.route('/profile', methods=['GET', 'POST'])
def profile(email, token):
    email = email.lower().strip()
    if call_validate_endpoint(email, token) == 200:
        if request.method == 'GET':
            has_profile = users.find_one({"_id": email})
            if not has_profile:
                resp = jsonify({"statusCode": 401, "body": "User Not found"})
                resp.status_code = 200
                return resp
            user_profile = users.find_one({"_id": email})
            dir_token = call_auth_endpoint()
            if dir_token != 400:
                name = get_name(dir_token, email)
            else:
                name = ""
            user_profile.update({"name": name})
            resp = jsonify({"statusCode": 200, "body": user_profile})
            resp.status_code = 200
            return resp
        elif request.method == 'POST':
            data = request.get_json(silent=True)
            if not data or 'skills' not in data or not data['skills']:
                resp = jsonify({"statusCode": 400, "body": "Required info not found"})
                resp.status_code = 400
                return resp
            if 'prizes' not in data:
                prizes = []
            else:
                prizes = format_string(data['prizes'].strip().lower())
            skills = format_string(data['skills'].strip().lower())
            user_exists = users.find_one({"_id": email})
            if user_exists:
                users.update({"_id": email}, {"$set": {"skills": skills, "prizes": prizes}})
                resp = jsonify({"statusCode": 200, "body": "Successful update"})
                resp.status_code = 200
            else:
                users.insert_one({"_id": email, "skills": skills, "prizes": prizes, "hasateam": False, "potentialteams": []})
                resp = jsonify({"statusCode": 201, "body": "Profile created"})
                resp.status_code = 201
            return resp
    else:
        resp = jsonify({"statusCode": 404, "body": "Invalid request"})
        resp.status_code = 404
        return resp


@app.route('/start-a-team', methods=['POST'])
def start_a_team(email, token):
    email = email.strip().lower()
    if call_validate_endpoint(email, token) == 200:
        if request.method == 'POST':
            data = request.get_json(silent=True)
            if not data or 'name' not in data or 'desc' not in data or 'skills' not in data or not data['name'] or not data['desc'] or not data['skills']:
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
            user_exists = users.find_one({"_id": email})
            if not user_exists:
                resp = jsonify({"statusCode": 403, "body": "Invalid user"})
                resp.status_code = 403
                return resp
            if team_exist:
                resp = jsonify({"statusCode": 401, "body": "Invalid name"})
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
                    teams.insert({"_id": team_name, "members": [email], "desc": team_desc, "partnerskills": formatted_skills, "prizes": formatted_prizes, "complete": False, "interested": []})
                    resp = jsonify({"statusCode": 200, "body": "Success"})
                    resp.status_code = 200
                    return resp
    else:
        resp = jsonify({"statusCode": 404, "body": "Invalid request"})
        resp.status_code = 404
        return resp


@app.route('/leave-team', methods=['POST'])
def leave_team(email, token):
    email = email.strip().lower()
    if call_validate_endpoint(email, token) == 200:
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
                teams.update_one({"_id": team_name}, {"$set": {"complete": False}})
            users.update_one({"_id": email}, {"$set": {"hasateam": False}})
            resp = jsonify({"statusCode": 200, "body": "Success"})
            resp.status_code = 200
            return resp
    else:
        resp = jsonify({"statusCode": 404, "body": "Invalid request"})
        resp.status_code = 404
        return resp


@app.route('/add-team-member', methods=['POST'])
def add_team_member(email, token):
    email = email.strip().lower()
    if call_validate_endpoint(email, token) == 200:
        if request.method == 'POST':
            data = request.get_json(silent=True)
            if not data or 'email' not in data or not data['email']:
                resp = jsonify({"statusCode": 400, "body": "Required info not found"})
                resp.status_code = 400
                return resp
            partner_email = data['email'].strip().lower()
            dir_token = call_auth_endpoint()
            if dir_token == 400:
                resp = jsonify({"statusCode": 401, "body": "auth endpoint failed"})
                resp.status_code = 401
                return resp
            if get_name(dir_token, partner_email) == 400:
                resp = jsonify({"statusCode": 402, "body": "Partner doesn't have a hackru account"})
                resp.status_code = 402
                return resp
            team = teams.find_one({"members": {"$all": [email]}})
            if not team:
                resp = jsonify({"statusCode": 405, "body": "User not in a team"})
                resp.status_code = 405
                return resp
            team_name = team['_id']
            team_size = len(team['members'])
            team_full = teams.find_one({"_id": team_name, "complete": True})
            if team_full or team_size >= 4:
                resp = jsonify({"statusCode": 403, "body": "Team complete"})
                resp.status_code = 403
                return resp
            user_exist = users.find_one({"_id": partner_email})
            if not user_exist:
                users.insert({"_id": partner_email, "hasateam": True, "skills": [], "prizes": []})
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
                    resp = jsonify({"statusCode": 406, "body": "Partner in a team"})
                    resp.status_code = 406
                    return resp
    else:
        resp = jsonify({"statusCode": 404, "body": "Invalid request"})
        resp.status_code = 404
        return resp


@app.route('/team-complete', methods=['POST'])
def team_complete(email, token):
    email = email.strip().lower()
    if call_validate_endpoint(email, token) == 200:
        if request.method == 'POST':
            team = teams.find_one({"members": {"$all": [email]}}, {"_id"})
            if not team:
                resp = jsonify({"statusCode": 401, "body": "User not in a team"})
                resp.status_code = 401
                return resp
            team_name = team['_id']
            teams.update_one({"_id": team_name}, {"$set": {"complete": True}})
            resp = jsonify({"statusCode": 200, "body": "Success"})
            resp.status_code = 200
            return resp
    else:
        resp = jsonify({"statusCode": 404, "body": "Invalid request"})
        resp.status_code = 404
        return resp


@app.route('/open-teams', methods=['GET'])
def open_teams(email, token):
    email = email.strip().lower()
    if call_validate_endpoint(email, token) == 200:
        if request.method == 'GET':
            data = request.get_json(silent=True)
            if not data or 'filter' not in data or not data['filter']:
                available_teams = teams.find({"complete": False})
                all_open_teams = []
                for x in available_teams:
                    all_open_teams.append(x)
                if not all_open_teams:
                    resp = jsonify({"statusCode": 400, "body": "No open teams"})
                    resp.status_code = 400
                    return resp
                resp = jsonify({"statusCode": 200, "body": all_open_teams})
                resp.status_code = 200
                return resp
            else:
                search = data['filter'].lower().strip()
                available_teams = teams.find({"complete": False, "$or": [
                        {"desc": {"$regex": ".*" + search + ".*"}},
                        {"partnerskills": {"$regex": ".*" + search + ".*"}},
                        {"prizes": {"$regex": ".*" + search + ".*"}}
                             ]
                    })
                all_open_teams = []
                for x in available_teams:
                    all_open_teams.append(x)
                if not all_open_teams:
                    resp = jsonify({"statusCode": 400, "body": "No open teams"})
                    resp.status_code = 400
                    return resp
                resp = jsonify({"statusCode": 200, "body": all_open_teams})
                resp.status_code = 200
                return resp
    else:
        resp = jsonify({"statusCode": 404, "body": "Invalid request"})
        resp.status_code = 404
        return resp


@app.route('/team-profile', methods=['GET'])
def team_profile(email, token):
    email = email.strip().lower()
    if call_validate_endpoint(email, token) == 200:
        if request.method == 'GET':
            team = teams.find_one({"members": {"$all": [email]}})
            if not team:
                resp = jsonify({"statusCode": 400, "body": "Team Not found"})
                resp.status_code = 400
            else:
                members = team['members']
                members_names = []
                for member in members:
                    token = call_auth_endpoint()
                    if token == 200:
                        continue
                    name = get_name(token, member)
                    if name == 200:
                        continue
                    members_names.append(name)
                    team.update({"names": members_names})
                resp = jsonify({"statusCode": 200, "body": team})
                resp.status_code = 200
            return resp
    else:
        resp = jsonify({"statusCode": 404, "body": "Invalid request"})
        resp.status_code = 404
        return resp


@app.route('/team-recommendations', methods=['GET'])
def team_recommendations(email, token):
    email = email.strip().lower()
    if call_validate_endpoint(email, token) == 200:
        if request.method == 'GET':
            user = users.find_one({"_id": email})
            if not user:
                resp = jsonify({"statusCode": 403, "body": "Invalid user"})
                resp.status_code = 403
                return resp
            user_in_a_team = users.find_one({"_id": email, "hasateam": True})
            if user_in_a_team:
                resp = jsonify({"statusCode": 401, "body": "User in a team"})
                resp.status_code = 401
                return resp
            if 'skills' not in user or not user['skills']:
                resp = jsonify({"statusCode": 400, "body": "No recommendations found"})
                resp.status_code = 400
                return resp
            if 'prizes' not in user or not user['prizes']:
                prizes = []
            else:
                prizes = user['prizes']
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

            for prize in prizes:
                match = teams.aggregate([
                    {"$match": {"complete": False, "pries": {"$all": [prize]}}}
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
    else:
        resp = jsonify({"statusCode": 404, "body": "Invalid request"})
        resp.status_code = 404
        return resp


@app.route('/individual-recommendations', methods=['GET'])
def individual_recommendations(email, token):
    email = email.strip().lower()
    if call_validate_endpoint(email, token) == 200:
        if request.method == 'GET':
            team = teams.find_one({"members": {"$all": [email]}})
            if not team:
                resp = jsonify({"statusCode": 400, "body": "User not in a team"})
                resp.status_code = 400
                return resp
            if 'partnerskills' not in team or not team['partnerskills']:
                resp = jsonify({"statusCode": 401, "body": "Profile not complete"})
                resp.status_code = 401
                return resp
            if 'prizes' not in team or not team['prizes']:
                prizes = []
            else:
                prizes = team['prizes']
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
                        dir_token = call_auth_endpoint()
                        if dir_token != 400:
                            name = get_name(dir_token, email)
                        else:
                            name = ""
                        m.update({"name": name})
                        matches.append(m)
            for prize in prizes:
                match = users.aggregate([
                    {"$match": {"hasateam": False, "prizes": {"$all": [prize]}}}
                ])
                if not match:
                    continue
                for m in match:
                    if m['_id'] not in emails:
                        emails.add(m['_id'])
                        dir_token = call_auth_endpoint()
                        if dir_token != 400:
                            name = get_name(dir_token, email)
                        else:
                            name = ""
                        m.update({"name": name})
                        matches.append(m)
            if not matches:
                resp = jsonify({"statusCode": 402, "body": "No recommendations found"})
                resp.status_code = 402
            else:
                resp = jsonify({"statusCode": 200, "body": matches})
                resp.status_code = 200
            return resp
    else:
        resp = jsonify({"statusCode": 404, "body": "Invalid request"})
        resp.status_code = 404
        return resp


@app.route('/interested', methods=['POST'])
def interested(email, token):
    email = email.strip().lower()
    if call_validate_endpoint(email, token) == 200:
        if request.method == 'POST':
            data = request.get_json(silent=True)
            if not data or 'name' not in data or not data['name']:
                resp = jsonify({"statusCode": 401, "body": "Missing inf"})
                resp.status_code = 401
                return resp
            user_in_a_team = users.find_one({"_id": email, "hasateam": True})
            if user_in_a_team:
                resp = jsonify({"statusCode": 403, "body": "User in a team"})
                resp.status_code = 403
                return resp
            team_name = data['name']
            team = teams.find_one({"_id": team_name})
            if not team:
                resp = jsonify({"statusCode": 402, "body": "Invalid name"})
                resp.status_code = 402
                return resp
            complete = teams.find_one({"_id": team_name, "complete": True})
            if complete or len(team['members']) >= 4:
                resp = jsonify({"statusCode": 405, "body": "Team complete"})
                resp.status_code = 405
                return resp
            teams.update_one({"_id": team_name}, {"$push": {"interested": email}})
            users.update_one({"_id": email}, {"$push": {"potentialteams": team_name}})
            resp = jsonify({"statusCode": 200, "body": "Success"})
            resp.status_code = 200
            return resp
    else:
        resp = jsonify({"statusCode": 404, "body": "Invalid request"})
        resp.status_code = 404
        return resp


@app.route('/confirm-member', methods=['POST'])
def confirm_member(email, token):
    email = email.strip().lower()
    if call_validate_endpoint(email, token) == 200:
        if request.method == 'POST':
            data = request.get_json(silent=True)
            if not data or 'email' not in data or not data['email']:
                resp = jsonify({"statusCode": 401, "body": "Missing inf"})
                resp.status_code = 401
                return resp
            hacker = data['email'].strip().lower()
            team_name = teams.find_one({"members": {"$all": [email]}}, {"_id"})['_id']
            team = teams.find_one({"_id": team_name})
            team_members = team['members']
            complete = teams.find_one({"_id": team_name, "complete": True})
            if len(team_members) >= 4 or complete:
                resp = jsonify({"statusCode": 402, "body": "Team Complete"})
                resp.status_code = 402
                return resp
            users.update_one({"_id": hacker}, {"$set": {"hasateam": True}})
            users.update_one({"_id": hacker}, {"$pull": {"potentialteams": team_name}})
            teams.update_one({"_id": team_name}, {"$push": {"members": hacker}})
            teams.update_one({"_id": team_name}, {"$pull": {"interested": hacker}})
            resp = jsonify({"statusCode": 200, "body": "Success"})
            resp.status_code = 200
            return resp
    else:
        resp = jsonify({"statusCode": 404, "body": "Invalid request"})
        resp.status_code = 404
        return resp

