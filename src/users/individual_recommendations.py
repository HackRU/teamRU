from src.flaskapp.lcs import call_auth_endpoint, get_name
from src.flaskapp.util import return_resp
from src.flaskapp.db import coll
from src.flaskapp.schemas import (
    ensure_json,
    ensure_user_logged_in,
    ensure_feature_is_enabled,
)


def get_individual_recommendations(email):  # GET
    team = coll("teams").find_one({"members": {"$all": [email]}})
    if not team:
        return return_resp(400, "User not in a team")
    if "partnerskills" not in team or not team["partnerskills"]:
        return return_resp(401, "Profile not complete")
    if "prizes" not in team or not team["prizes"]:
        prizes = []
    else:
        prizes = team["prizes"]
    skills = team["partnerskills"]
    emails = set()
    matches = []
    for skill in skills:
        match = coll("users").aggregate(
            [{"$match": {"hasateam": False, "skills": {"$all": [skill]}}}]
        )
        if not match:
            continue
        for m in match:
            if m["_id"] not in emails:
                emails.add(m["_id"])
                dir_token = call_auth_endpoint()
                if dir_token != 400:
                    name = get_name(dir_token, email)
                else:
                    name = ""
                m.update({"name": name})
                matches.append(m)
    for prize in prizes:
        match = coll("users").aggregate(
            [{"$match": {"hasateam": False, "prizes": {"$all": [prize]}}}]
        )
        if not match:
            continue
        for m in match:
            if m["_id"] not in emails:
                emails.add(m["_id"])
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
