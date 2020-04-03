from app.util import call_validate_endpoint, return_resp
from flask import request
from app.db import teams


def mark_team_complete(email, token):
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