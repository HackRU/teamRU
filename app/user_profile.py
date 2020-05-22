from app.util import return_resp, format_string
from flask import request
from app.lcs import call_auth_endpoint, get_name
from app.db import coll
from app.schemas import ensure_json, ensure_user_logged_in, ensure_feature_is_enabled


@ensure_json()
@ensure_user_logged_in()
@ensure_feature_is_enabled("user profile")
def update_profile():
    if request.method == 'GET':
        data = request.get_json(silent=True)
        email = data['user_email']
        email = email.strip().lower()
        has_profile = coll("users").find_one({"_id": email})
        if not has_profile:
            return return_resp(200, "User Not found")
        user_profile = coll("users").find_one({"_id": email})
        dir_token = call_auth_endpoint()
        if dir_token != 400:
            name = get_name(dir_token, email)
        else:
            name = ""
        user_profile.update({"name": name})
        return return_resp(200, user_profile)
    elif request.method == 'POST':
        data = request.get_json(silent=True)
        email = data['user_email']
        email = email.strip().lower()
        if not data or 'skills' not in data or not data['skills']:
            return return_resp(400, "Required info not found")
        if 'prizes' not in data:
            prizes = []
        else:
            prizes = format_string(data['prizes'].strip().lower())
        skills = format_string(data['skills'].strip().lower())
        user_exists = coll("users").find_one({"_id": email})
        if user_exists:
            coll("users").update({"_id": email}, {"$set": {"skills": skills, "prizes": prizes}})
            return return_resp(200, "Successful update")
        else:
            coll("users").insert_one(
                {"_id": email, "skills": skills, "prizes": prizes, "hasateam": False, "potentialteams": []})
            return return_resp(201, "Profile created")
