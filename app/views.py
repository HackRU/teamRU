from flask import render_template, request
import requests
from app import app
from app.db import users, teams

base_url = ""


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


def call_auth_endpoint(email, password):
    data_dic = {"email": email, "token": password}
    resp = requests.post(base_url + "/authorize", json=data_dic)
    if not resp:
        return 400
    resp_parsed = resp.json()
    if resp_parsed["statusCode"] == 200:
        return resp_parsed["auth"]["token"]


def get_name(dir_email, token, email):
    data_dic = {"email": dir_email, "token": token, "query": {"email": email}}
    resp = requests.post(base_url + "/read", json=data_dic)
    if not resp:
        return 400
    resp_parsed = resp.json()
    return resp_parsed["body"]['first_name'] + "" + resp_parsed["body"]['last_name'] + ""


def format_string(s):
    if not s:
        return []
    elements = s.split(",")
    for ele in elements:
        ele.strip()
    return elements


@app.route('/start-a-team', methods=['POST'])
def start_a_team(email, token):
    if call_validate_endpoint(email, token) == 200:
        if request.method == 'POST':
            data = request.get_json(silent=True)
            if not data:
                return {"statusCode": 400, "body": "Required info not found"}
            if 'name' or 'desc' or 'skills' not in data:
                return {"statusCode": 400, "body": "Required info not found"}
            if 'prizes' in data:
                prizes = data['prizes'].strip().lower()
            else:
                prizes = None
            team_name = data['name'].strip().lower()
            team_desc = data['desc'].strip().lower()
            partnerskills = data['skills'].strip().lower()
            team_exist = teams.find_one({"_id": team_name})
            if team_exist:
                return {"statusCode": 401, "body": "Another team with this name already exists"}
            else:
                user_exist = users.find_one({"_id": email})
                if user_exist:
                    user_in_a_team = users.find_one({"_id": email, "hasateam": True})
                    if user_in_a_team:
                        return {"statusCode": 402, "body": "You can't start a team while you are in a team"}
                    else:
                        users.update_one({"_id": email}, {"$set": {"hasateam": True}})
                else:
                    users.insert({"_id": email, "hasateam": True})
                teams.insert({"_id": team_name, "members": [email], "desc": team_desc, "partnerskills": partnerskills, "prizes": prizes, "complete": False})
                return {"statusCode": 200, "body": "Success"}
    else:
        return {"statusCode": 403, "body": "Invalid request"}


@app.route('/leave-team', methods=['POST'])
def leave_team(email, token):
    if call_validate_endpoint(email, token) == 200:
        if request.method == 'POST':
            team_name = teams.find_one({"members": {"$all": [email]}}, {"_id"})['_id']
            team_size = len(teams.find_one({"_id": team_name})['members'])
            if team_size == 1:
                teams.delete_one({"_id": team_name})
            else:
                teams.update_one({"_id": team_name}, {"$pull": {"members": email}})
            users.update_one({"_id": email}, {"$set": {"hasateam": False}})
        return {"statusCode": 200, "body": "Success"}
    else:
        return {"statusCode": 403, "body": "Invalid request"}


@app.route('/add-team-member', methods=['POST'])
def add_team_member(email, token):
    if call_validate_endpoint(email, token) == 200:
        if request.method == 'POST':
            data = request.get_json(silent=True)
            if not data:
                return {"statusCode": 400, "body": "Required info not found"}
            if 'email' not in data:
                return {"statusCode": 400, "body": "Required info not found"}
            partner_email = data['email'].strip().lower()
            dir_email = ""
            password = ""
            dir_token = call_auth_endpoint(dir_email, password)
            if dir_token is not 400:
                if not get_name(dir_email, dir_token, email):
                    return {"statusCode": 405, "body": "This person doesn't have a hackru profile"}
            team_name = teams.find_one({"members": {"$all": [email]}}, {"_id"})['_id']
            team_size = len(teams.find_one({"_id": team_name})['members'])
            if team_size >= 4:
                return {"statusCode": 401, "body": "A team can\'t have more than 4 members"}
            team_complete = teams.find_one({"_id": team_name})['complete']
            if team_complete is True:
                return {"statusCode": 401, "body": "Team is complete"}
            user_exist = users.find_one({"_id": partner_email})
            if not user_exist:
                users.insert({"_id": partner_email, "hasateam": True})
                teams.update_one({"_id": team_name}, {"$push": {"members": partner_email}})
                return {"statusCode": 200, "body": "Success"}
            else:
                partner_in_a_team = users.find_one({"_id": partner_email, "hasateam": True})
                if not partner_in_a_team:
                    users.update_one({"_id": partner_email}, {"$set": {"hasateam": True}})
                    teams.update_one({"_id": team_name}, {"$push": {"members": partner_email}})
                    return {"statusCode": 200, "body": "Success"}
                else:
                    return {"statusCode": 402, "body": "This person is already in a team"}
    else:
        return {"statusCode": 403, "body": "Invalid request"}


@app.route('/team-complete', methods=['POST'])
def team_complete(email, token):
    if call_validate_endpoint(email, token) == 200:
        if request.method == 'POST':
            team_name = teams.aggregate([
                {"$match": {"_id": email}}, {"$project": {"_id": 1}}
            ])
            teams.update_one({"_id": team_name}, {"$set": {"complete": True}})
            return {"statusCode": 200, "body": "Success"}
    else:
        return {"statusCode": 403, "body": "Invalid request"}


@app.route('/profile', methods=['GET', 'POST'])
def profile(email, token):
    #GET is used to get a profile while POST is used to create and update a profile
    if call_validate_endpoint(email, token) == 200:
        if request.method == 'GET':
            has_profile = users.find_one({"_id": email})
            if not has_profile:
                return {"statusCode": 403, "body": "No profile"}
            user_profile = users.find_one({"_id": email})
            return {"statusCode": 200, "body": user_profile}
        elif request.method == 'POST':
            data = request.get_json(silent=True)
            if not data:
                return {"statusCode": 400, "body": "Required info not found"}
            if 'skills' not in data:
                return {"statusCode": 400, "body": "Required info not found"}
            skills = data['skills'].strip().lower()
            if 'prizes' not in data:
                prizes = None
            else:
                prizes = data['prizes'].strip().lower()
            #Enter the skills separated by a comma. example: java, flask, backend
            formatted_skills = format_string(skills)
            user_exists = users.find({"_id": email})
            if user_exists:
                users.update({"_id": email}, {"$set": {"skills": formatted_skills, "prizes": prizes}})
                return {"statusCode": 200, "body": "Success"}
            users.insert_one({"_id": email, "skills": formatted_skills, "prizes": prizes})
            return {"statusCode": 200, "body": "Success"}
    else:
        return {"statusCode": 403, "body": "Invalid request"}


@app.route('/teams', methods=['GET'])
def teams(email, token):
    if call_validate_endpoint(email, token) == 200:
        if request.method == 'POST':
            data = request.get_json(silent=True)
            if not data:
                open_teams = teams.find({"complete": False})
                if not open_teams:
                    return {"statusCode": 400, "body": "No open teams"}
                # all open teams -> edit response later
                return {"statusCode": 200, "body": open_teams}
            filter = data['filter']
            # we can also change this to multiple filters in the future
            open_teams = teams.find({"complete": False, '$or': [
                {"desc": {"$regex": ".*" + filter + ".*"}},
                {"skills": {"$regex": ".*" + filter + ".*"}},
                {"prizes": {"$regex": ".*" + filter + ".*"}}
                                     ]})
            if not open_teams:
                return {"statusCode": 400, "body": "No open teams"}
            return {"statusCode": 200, "body": open_teams}
    else:
        return {"statusCode": 403, "body": "Invalid request"}


@app.route('/team-members', methods=['GET'])
def team_members(email, token):
    pass


@app.route('/interested', methods=['POST'])
def interested(email, token):
    pass


@app.route('/confirm-member', methods=['POST'])
def confirm_member(email, token):
    pass


@app.route('/team-recommendations', methods=['GET'])
def team_recommendations(email, token):
    pass


@app.route('/recommendations', methods=['GET'])
def recommendations(email, token):
    pass





"""""OLD design"""


@app.route('/get-recommendations', methods=['GET'])
def get_recommendations(email, token):
    if call_validate_endpoint(email, token) == 200:
        if request.method == 'GET':
            tracks = users.aggregate([
                {"$match": {"_id": email}}, {"$project": {"tracks": 1}}
            ])
            partner_skills = users.aggregate([
                {"$match": {"_id": email}}, {"$project": {"partner_skills": 1}}
            ])
            matches_emails = set()
            matches = []
            for track in tracks:
                match = users.aggregate([
                    {"hasateam": False, "tracks": {"$all": [track]}}, {"$project": {"email": 1, "skills": 1, "tracks": 1}}
                ])
                if not match:
                    continue
                else:
                    match_email = match['email']
                    if match_email not in matches_emails:
                        matches_emails.add(match_email)
                        matches.append(match)
            for skill in partner_skills:
                match = users.aggregate([
                    {"hasateam": False, "skills": {"$all": [skill]}}, {"$project": {"email": 1, "skills": 1, "tracks": 1}}
                ])
                if not match:
                    continue
                else:
                    match_email = match['email']
                    if match_email not in matches_emails:
                        matches_emails.add(match_email)
                        matches.append(match)
            if not matches:
                return render_template('', result='We couldn\'t find any members that match your criteria, try adding more skills')
            else:
                return render_template('', matches=matches)
    else:
        return render_template('', result='Please try again')


@app.route('/contact-person', methods=['POST'])
def contact_team(email, token):
    # Goal is to use the dm endpoint from lcs
    '''Not yet implemented'''
    if call_validate_endpoint(email, token) == 200:
        if request.method == 'POST':
            user_email = request.form['email']
            if not user_email:
                return render_template('', result='Please try again')
            slack_id = users.aggregate([{"match": {"_id": user_email}}, {"$project": {"slack_id": 1}}])
            if not slack_id:
                return render_template('', result='Please try again')
            return render_template('', slack_id=slack_id)
    else:
        return render_template('', result='Please try again')
