from flask import request
from app import app
from app.db import users, teams
from app.profile import update_profile

from app.util import call_validate_endpoint, login, call_auth_endpoint, get_name, format_string, return_resp


@app.route('/profile', methods=['GET', 'POST'])
def profile(email, token):
    update_profile(email, token)


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
                return return_resp(403, "Invalid user")
            if team_exist:
                return return_resp(401, "Invalid name")
            else:
                user_in_a_team = users.find_one({"_id": email, "hasateam": True})
                if user_in_a_team:
                    return return_resp(402, "User in a team")
                else:
                    users.update_one({"_id": email}, {"$set": {"hasateam": True}})
                    teams.insert({"_id": team_name, "members": [email], "desc": team_desc, "partnerskills": formatted_skills, "prizes": formatted_prizes, "complete": False, "interested": []})
                    return return_resp(200, "Success")
    else:
        return return_resp(404, "Invalid request")


@app.route('/leave-team', methods=['POST'])
def leave_team(email, token):
    email = email.strip().lower()
    if call_validate_endpoint(email, token) == 200:
        if request.method == 'POST':
            user_in_a_team = users.find_one({"_id": email, "hasateam": True})
            if not user_in_a_team:
                return return_resp(400, "User doesn't have a tram")
            team_name = teams.find_one({"members": {"$all": [email]}}, {"_id"})['_id']
            team_size = len(teams.find_one({"_id": team_name})['members'])
            if team_size == 1:
                teams.delete_one({"_id": team_name})
            else:
                teams.update_one({"_id": team_name}, {"$pull": {"members": email}})
                teams.update_one({"_id": team_name}, {"$set": {"complete": False}})
            users.update_one({"_id": email}, {"$set": {"hasateam": False}})
            return return_resp(200, "Success")
    else:
        return return_resp(404, "Invalid request")


@app.route('/add-team-member', methods=['POST'])
def add_team_member(email, token):
    email = email.strip().lower()
    if call_validate_endpoint(email, token) == 200:
        if request.method == 'POST':
            data = request.get_json(silent=True)
            if not data or 'email' not in data or not data['email']:
                return return_resp(400, "Required info not found")
            partner_email = data['email'].strip().lower()
            dir_token = call_auth_endpoint()
            if dir_token == 400:
                return return_resp(401, "auth endpoint failed")
            if get_name(dir_token, partner_email) == 400:
                return return_resp(402, "Partner doesn't have a hackru account")
            team = teams.find_one({"members": {"$all": [email]}})
            if not team:
                return return_resp(405, "User not in a team")
            team_name = team['_id']
            team_size = len(team['members'])
            team_full = teams.find_one({"_id": team_name, "complete": True})
            if team_full or team_size >= 4:
                return return_resp(403, "Team complete")
            user_exist = users.find_one({"_id": partner_email})
            if not user_exist:
                users.insert({"_id": partner_email, "hasateam": True, "skills": [], "prizes": []})
                teams.update_one({"_id": team_name}, {"$push": {"members": partner_email}})
                return return_resp(200, "Success")
            else:
                partner_in_a_team = users.find_one({"_id": partner_email, "hasateam": True})
                if not partner_in_a_team:
                    users.update_one({"_id": partner_email}, {"$set": {"hasateam": True}})
                    teams.update_one({"_id": team_name}, {"$push": {"members": partner_email}})
                    if team_size == 4:
                        teams.update_one({"_id": team_name}, {"$set": {"complete": True}})
                    return return_resp(200, "Success")
                else:
                    return return_resp(406, "Partner in a team")
    else:
        return return_resp(404, "Invalid request")


@app.route('/team-complete', methods=['POST'])
def team_complete(email, token):
    email = email.strip().lower()
    if call_validate_endpoint(email, token) == 200:
        if request.method == 'POST':
            team = teams.find_one({"members": {"$all": [email]}}, {"_id"})
            if not team:
                return return_resp(401, "User not in a team")
            team_name = team['_id']
            teams.update_one({"_id": team_name}, {"$set": {"complete": True}})
            return return_resp(200, "Success")
    else:
        return return_resp(404, "Invalid request")


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
                    return return_resp(400, "No open teams")
                return return_resp(200, all_open_teams)
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
                    return return_resp(400, "No open teams")
                return return_resp(200, all_open_teams)
    else:
        return return_resp(404, "Invalid request")


@app.route('/team-profile', methods=['GET'])
def team_profile(email, token):
    email = email.strip().lower()
    if call_validate_endpoint(email, token) == 200:
        if request.method == 'GET':
            team = teams.find_one({"members": {"$all": [email]}})
            if not team:
                return return_resp(400, "Team Not found")
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
                return return_resp(200, team)
    else:
        return return_resp(404, "Invalid request")


@app.route('/team-recommendations', methods=['GET'])
def team_recommendations(email, token):
    email = email.strip().lower()
    if call_validate_endpoint(email, token) == 200:
        if request.method == 'GET':
            user = users.find_one({"_id": email})
            if not user:
                return return_resp(403, "Invalid user")
            user_in_a_team = users.find_one({"_id": email, "hasateam": True})
            if user_in_a_team:
                return return_resp(402, "User in a team")
            if 'skills' not in user or not user['skills']:
                return return_resp(400, "No recommendations found")
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
                return return_resp(400, "No recommendations found")
            else:
                return return_resp(200, matches)
    else:
        return return_resp(404, "Invalid request")


@app.route('/individual-recommendations', methods=['GET'])
def individual_recommendations(email, token):
    email = email.strip().lower()
    if call_validate_endpoint(email, token) == 200:
        if request.method == 'GET':
            team = teams.find_one({"members": {"$all": [email]}})
            if not team:
                return return_resp(400, "User not in a team")
            if 'partnerskills' not in team or not team['partnerskills']:
                return return_resp(401, "Profile not complete")
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
                return return_resp(402, "No recommendations found")
            else:
                return return_resp(200, matches)
    else:
        return return_resp(404, "Invalid request")


@app.route('/interested', methods=['POST'])
def interested(email, token):
    email = email.strip().lower()
    if call_validate_endpoint(email, token) == 200:
        if request.method == 'POST':
            data = request.get_json(silent=True)
            if not data or 'name' not in data or not data['name']:
                return return_resp(401, "Missing inf")
            user_in_a_team = users.find_one({"_id": email, "hasateam": True})
            if user_in_a_team:
                return return_resp(403, "User in a team")
            team_name = data['name']
            team = teams.find_one({"_id": team_name})
            if not team:
                return return_resp(402, "Invalid name")
            complete = teams.find_one({"_id": team_name, "complete": True})
            if complete or len(team['members']) >= 4:
                return return_resp(405, "Team complete")
            teams.update_one({"_id": team_name}, {"$push": {"interested": email}})
            users.update_one({"_id": email}, {"$push": {"potentialteams": team_name}})
            return return_resp(200, "Success")
    else:
        return return_resp(404, "Invalid request")


@app.route('/confirm-member', methods=['POST'])
def confirm_member(email, token):
    email = email.strip().lower()
    if call_validate_endpoint(email, token) == 200:
        if request.method == 'POST':
            data = request.get_json(silent=True)
            if not data or 'email' not in data or not data['email']:
                return return_resp(401, "Missing inf")
            hacker = data['email'].strip().lower()
            team_name = teams.find_one({"members": {"$all": [email]}}, {"_id"})['_id']
            team = teams.find_one({"_id": team_name})
            team_members = team['members']
            complete = teams.find_one({"_id": team_name, "complete": True})
            if len(team_members) >= 4 or complete:
                return return_resp(402, "Team Complete")
            users.update_one({"_id": hacker}, {"$set": {"hasateam": True}})
            users.update_one({"_id": hacker}, {"$pull": {"potentialteams": team_name}})
            teams.update_one({"_id": team_name}, {"$push": {"members": hacker}})
            teams.update_one({"_id": team_name}, {"$pull": {"interested": hacker}})
            return return_resp(200, "Success")
    else:
        return return_resp(404, "Invalid request")

