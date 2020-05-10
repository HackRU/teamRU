from app.util import call_validate_endpoint, return_resp, coll
from flask import request


def confirm(email, token):
    email = email.strip().lower()
    if call_validate_endpoint(email, token) != 200:
        return return_resp(404, "Invalid request")
    else:
        if request.method == 'POST':
            data = request.get_json(silent=True)
            if not data or 'email' not in data or not data['email']:
                return return_resp(401, "Missing inf")
            hacker = data['email'].strip().lower()
            team_name = coll("teams").find_one({"members": {"$all": [email]}}, {"_id"})['_id']
            team = coll("teams").find_one({"_id": team_name})
            team_members = team['members']
            complete = coll("teams").find_one({"_id": team_name, "complete": True})
            if len(team_members) >= 4 or complete:
                return return_resp(402, "Team Complete")
            coll("users").update_one({"_id": hacker}, {"$set": {"hasateam": True}})
            coll("users").update_one({"_id": hacker}, {"$pull": {"potentialteams": team_name}})
            coll("teams").update_one({"_id": team_name}, {"$push": {"members": hacker}})
            coll("teams").update_one({"_id": team_name}, {"$pull": {"interested": hacker}})
            return return_resp(200, "Success")
