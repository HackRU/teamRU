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


@app.route('/team-members', methods=['GET'])
def team_members(email="", token=""):
    # if call_validate_endpoint(email, token) == 200:
        if request.method == 'GET':
            members = teams.find_one({"members": {"$all": [email]}}, {"members"})['members']
            resp = jsonify({"statusCode": 200, "body": members})
            resp.status_code = 200
            return resp
    # else:
    #     resp = jsonify({"statusCode": 404, "body": "Invalid request"})
    #     resp.status_code = 404
    #     return resp






"""endpoints below not done yet"""

#
# @app.route('/interested', methods=['POST'])
# def interested(email, token):
#     # if call_validate_endpoint(email, token) == 200:
#
#     # else:
#     #     resp = jsonify({"statusCode": 404, "body": "Invalid request"})
#     #     resp.status_code = 404
#     #     return resp

#
# @app.route('/confirm-member', methods=['POST'])
# def confirm_member(email, token):
#     pass
#
#
# @app.route('/team-recommendations', methods=['GET'])
# def team_recommendations(email, token):
#     pass
#
#
#
# @app.route('/individual-recommendations', methods=['GET'])
# def individual_recommendations(email="hi", token=""):
#     # if call_validate_endpoint(email, token) == 200:
#         if request.method == 'GET':
#             prizes = users.aggregate([
#                 {"$match": {"_id": email}}, {"$project": {"prizes": 1}}
#             ])
#             partner_skills = users.aggregate([
#                 {"$match": {"_id": email}}, {"$project": {"partner_skills": 1}}
#             ])
#             matches_emails = set()
#             matches = []
#             for track in prizes:
#                 match = users.aggregate([
#                     {"hasateam": False, "prizes": {"$all": [track]}}, {"$project": {"email": 1, "skills": 1, "prizes": 1}}
#                 ])
#                 if not match:
#                     continue
#                 else:
#                     match_email = match['email']
#                     if match_email not in matches_emails:
#                         matches_emails.add(match_email)
#                         matches.append(match)
#             for skill in partner_skills:
#                 match = users.aggregate([
#                     {"hasateam": False, "skills": {"$all": [skill]}}, {"$project": {"email": 1, "skills": 1, "prizes": 1}}
#                 ])
#                 if not match:
#                     continue
#                 else:
#                     match_email = match['email']
#                     if match_email not in matches_emails:
#                         matches_emails.add(match_email)
#                         matches.append(match)
#             if not matches:
#                 resp = jsonify({"statusCode": 400, "body": "No recommendations found"})
#                 resp.status_code = 400
#                 return resp
#             else:
#                 resp = jsonify({"statusCode": 200, "body": matches})
#                 resp.status_code = 200
#                 return resp
    # else:
    #     resp = jsonify({"statusCode": 404, "body": "Invalid request"})
    #     resp.status_code = 404
    #     return resp
#
#
# @app.route('/contact-person', methods=['POST'])
# def contact_team(email, token):
#     # Goal is to use the dm endpoint from lcs
#     '''Not yet implemented'''
#     if call_validate_endpoint(email, token) == 200:
#         if request.method == 'POST':
#             user_email = request.form['email']
#             if not user_email:
#                 return render_template('', result='Please try again')
#             slack_id = users.aggregate([{"match": {"_id": user_email}}, {"$project": {"slack_id": 1}}])
#             if not slack_id:
#                 return render_template('', result='Please try again')
#             return render_template('', slack_id=slack_id)
#     else:
#         return render_template('', result='Please try again')