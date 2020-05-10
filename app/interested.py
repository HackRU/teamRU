from app.util import call_validate_endpoint, return_resp, coll
from flask import request


def user_interested(email, token):
    email = email.strip().lower()
    if call_validate_endpoint(email, token) != 200:
        return return_resp(404, "Invalid request")
    else:
        if request.method == 'POST':
            data = request.get_json(silent=True)
            if not data or 'name' not in data or not data['name']:
                return return_resp(401, "Missing inf")
            user_in_a_team = coll("users").find_one({"_id": email, "hasateam": True})
            if user_in_a_team:
                return return_resp(403, "User in a team")
            team_name = data['name']
            team = coll("teams").find_one({"_id": team_name})
            if not team:
                return return_resp(402, "Invalid name")
            complete = coll("teams").find_one({"_id": team_name, "complete": True})
            if complete or len(team['members']) >= 4:
                return return_resp(405, "Team complete")
            coll("teams").update_one({"_id": team_name}, {"$push": {"interested": email}})
            coll("users").update_one({"_id": email}, {"$push": {"potentialteams": team_name}})
            return return_resp(200, "Success")
