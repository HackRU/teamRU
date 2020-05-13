from app.util import call_validate_endpoint, return_resp, coll, validate_feature_is_enabled
from flask import request


@validate_feature_is_enabled("team recommendations")
def get_team_recommendations():
    if request.method == 'GET':
        data = request.get_json(silent=True)
        if not data or 'user_email' not in data or not data['user_email'] or 'token' not in data or not data['token']:
            return return_resp(408, "Missing email or token")
        email = data['user_email']
        token = data['token']
        email = email.strip().lower()
        if call_validate_endpoint(email, token) != 200:
            return return_resp(404, "Invalid request")
        user = coll("users").find_one({"_id": email})
        if not user:
            return return_resp(403, "Invalid user")
        user_in_a_team = coll("users").find_one({"_id": email, "hasateam": True})
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
            match = coll("teams").aggregate([
                {"$match": {"complete": False, "partnerskills": {"$all": [skill]}}}
            ])
            if not match:
                continue
            for m in match:
                if m['_id'] not in names:
                    names.add(m['_id'])
                    matches.append(m)

        for prize in prizes:
            match = coll("teams").aggregate([
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
