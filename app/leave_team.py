from app.util import call_validate_endpoint, return_resp, coll, validate_feature_is_enabled
from flask import request


@validate_feature_is_enabled("leave team")
def leave():
    if request.method == 'POST':
        data = request.get_json(silent=True)
        if not data or 'user_email' not in data or not data['user_email'] or 'token' not in data or not data['token']:
            return return_resp(408, "Missing email or token")
        email = data['user_email']
        token = data['token']
        email = email.strip().lower()
        if call_validate_endpoint(email, token) != 200:
            return return_resp(404, "Invalid request")
        user_in_a_team = coll("users").find_one({"_id": email, "hasateam": True})
        if not user_in_a_team:
            return return_resp(400, "User doesn't have a tram")
        team_name = coll("teams").find_one({"members": {"$all": [email]}}, {"_id"})['_id']
        team_size = len(coll("teams").find_one({"_id": team_name})['members'])
        if team_size == 1:
            coll("teams").delete_one({"_id": team_name})
        else:
            coll("teams").update_one({"_id": team_name}, {"$pull": {"members": email}})
            coll("teams").update_one({"_id": team_name}, {"$set": {"complete": False}})
        coll("users").update_one({"_id": email}, {"$set": {"hasateam": False}})
        return return_resp(200, "Success")
