from flask import request

from src.flaskapp.util import return_resp
from src.flaskapp.db import coll
from src.flaskapp.schemas import ensure_json, ensure_user_logged_in, ensure_feature_is_enabled

def leave(email):
    if request.method == "POST":
        user_in_a_team = coll("users").find_one({"_id": email, "hasateam": True})
        if not user_in_a_team:
            return return_resp(400, "User doesn't have a tram")
        team_name = coll("teams").find_one({"members": {"$all": [email]}}, {"_id"})[
            "_id"
        ]
        team_size = len(coll("teams").find_one({"_id": team_name})["members"])
        if team_size == 1:
            coll("teams").delete_one({"_id": team_name})
        else:
            coll("teams").update_one({"_id": team_name}, {"$pull": {"members": email}})
            coll("teams").update_one({"_id": team_name}, {"$set": {"complete": False}})
        coll("users").update_one({"_id": email}, {"$set": {"hasateam": False}})
        return return_resp(200, "Success")
