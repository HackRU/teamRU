from flask import request

from src.flaskapp.util import return_resp
from src.flaskapp.db import coll
from src.flaskapp.schemas import ensure_json, ensure_user_logged_in, ensure_feature_is_enabled

def get_team_recommendations(email):
    if request.method == "GET":
        user = coll("users").find_one({"_id": email})
        if not user:
            return return_resp(403, "Invalid user")
        user_in_a_team = coll("users").find_one({"_id": email, "hasateam": True})
        if user_in_a_team:
            return return_resp(402, "User in a team")
        if "skills" not in user or not user["skills"]:
            return return_resp(400, "No recommendations found")
        if "prizes" not in user or not user["prizes"]:
            prizes = []
        else:
            prizes = user["prizes"]
        skills = user["skills"]
        names = set()
        matches = []
        for skill in skills:
            match = coll("teams").aggregate(
                [{"$match": {"complete": False, "partnerskills": {"$all": [skill]}}}]
            )
            if not match:
                continue
            for m in match:
                if m["_id"] not in names:
                    names.add(m["_id"])
                    matches.append(m)

        for prize in prizes:
            match = coll("teams").aggregate(
                [{"$match": {"complete": False, "pries": {"$all": [prize]}}}]
            )
            if not match:
                continue
            for m in match:
                if m["_id"] not in names:
                    names.add(m["_id"])
                    matches.append(m)
        if not matches:
            return return_resp(400, "No recommendations found")
        else:
            return return_resp(200, matches)
