from app.util import return_resp
from flask import request
from app.db import coll
from app.schemas import ensure_json, ensure_user_logged_in, ensure_feature_is_enabled


def user_interested(email, team_name):
    if request.method == "POST":
        user_in_a_team = coll("users").find_one({"_id": email, "hasateam": True})
        if user_in_a_team:
            return return_resp(403, "User in a team")
        team = coll("teams").find_one({"_id": team_name})
        if not team:
            return return_resp(402, "Invalid name")
        complete = coll("teams").find_one({"_id": team_name, "complete": True})
        if complete or len(team["members"]) >= 4:
            return return_resp(405, "Team complete")
        coll("teams").update_one({"_id": team_name}, {"$push": {"interested": email}})
        coll("users").update_one(
            {"_id": email}, {"$push": {"potentialteams": team_name}}
        )
        return return_resp(200, "Success")
