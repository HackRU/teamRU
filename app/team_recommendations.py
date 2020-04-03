from app.util import call_validate_endpoint, return_resp, call_auth_endpoint, get_name, format_string
from flask import request
from app.db import users, teams


def get_team_recommendations(email, token):
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