from app.util import return_resp
from flask import request
from app.lcs import call_auth_endpoint, get_name
from app.db import coll
from app.schemas import ensure_json, ensure_user_logged_in, ensure_feature_is_enabled


@ensure_json()
@ensure_user_logged_in()
@ensure_feature_is_enabled("individual recommendations")
def get_individual_recommendations():
    if request.method == 'GET':
        data = request.get_json(silent=True)
        email = data['user_email']
        email = email.strip().lower()
        team = coll("teams").find_one({"members": {"$all": [email]}})
        if not team:
            return return_resp(400, "User not in a team")
        if 'partnerskills' not in team or not team['partnerskills']:
            return return_resp(401, "Profile not complete")
        if 'prizes' not in team or not team['prizes']:
            prizes = []
        else:
            prizes = team['prizes']
        skills = team['partnerskills']
        emails = set()
        matches = []
        for skill in skills:
            match = coll("users").aggregate([
                {"$match": {"hasateam": False, "skills": {"$all": [skill]}}}
            ])
            if not match:
                continue
            for m in match:
                if m['_id'] not in emails:
                    emails.add(m['_id'])
                    dir_token = call_auth_endpoint()
                    if dir_token != 400:
                        name = get_name(dir_token, email)
                    else:
                        name = ""
                    m.update({"name": name})
                    matches.append(m)
        for prize in prizes:
            match = coll("users").aggregate([
                {"$match": {"hasateam": False, "prizes": {"$all": [prize]}}}
            ])
            if not match:
                continue
            for m in match:
                if m['_id'] not in emails:
                    emails.add(m['_id'])
                    dir_token = call_auth_endpoint()
                    if dir_token != 400:
                        name = get_name(dir_token, email)
                    else:
                        name = ""
                    m.update({"name": name})
                    matches.append(m)
        if not matches:
            return return_resp(402, "No recommendations found")
        else:
            return return_resp(200, matches)
