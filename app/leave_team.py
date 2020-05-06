from app.util import call_validate_endpoint, return_resp
from flask import request
from app.db import users, teams


def leave(email, token):
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