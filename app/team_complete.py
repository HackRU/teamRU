from app.util import call_validate_endpoint, return_resp
from flask import request
from app.db import teams


def mark_team_complete(email, token):
    email = email.strip().lower()
    if call_validate_endpoint(email, token) != 200:
        return return_resp(404, "Invalid request")
    else:
        if request.method == 'POST':
            team = teams.find_one({"members": {"$all": [email]}})
            if not team:
                return return_resp(401, "User not in a team")
            team_name = team['_id']
            team_complete = team['complete']
            if team_complete is True:
                teams.update_one({"_id": team_name}, {"$set": {"complete": False}})
                return return_resp(200, "False")
            else:
                teams.update_one({"_id": team_name}, {"$set": {"complete": True}})
                return return_resp(200, "True")
