from app.util import call_validate_endpoint, return_resp, coll, validate_feature_is_enabled
from flask import request


@validate_feature_is_enabled("team complete")
def mark_team_complete():
    if request.method == 'POST':
        data = request.get_json(silent=True)
        if not data or 'user_email' not in data or not data['user_email'] or 'token' not in data or not data['token']:
            return return_resp(408, "Missing email or token")
        email = data['user_email']
        token = data['token']
        email = email.strip().lower()
        if call_validate_endpoint(email, token) != 200:
            return return_resp(404, "Invalid request")
        team = coll("teams").find_one({"members": {"$all": [email]}})
        if not team:
            return return_resp(401, "User not in a team")
        team_name = team['_id']
        team_complete = team['complete']
        if team_complete is True:
            coll("teams").update_one({"_id": team_name}, {"$set": {"complete": False}})
            return return_resp(200, "False")
        else:
            coll("teams").update_one({"_id": team_name}, {"$set": {"complete": True}})
            return return_resp(200, "True")
