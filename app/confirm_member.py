from app.util import call_validate_endpoint, return_resp, coll, validate_feature_is_enabled
from flask import request


@validate_feature_is_enabled("confirm member")
def confirm():
    if request.method == 'POST':
        data = request.get_json(silent=True)
        if not data or 'user_email' not in data or not data['user_email'] or 'token' not in data or not data['token']:
            return return_resp(408, "Missing email or token")
        email = data['user_email']
        token = data['token']
        email = email.strip().lower()
        if call_validate_endpoint(email, token) != 200:
            return return_resp(404, "Invalid request")
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
