from flask import request

from src.flaskapp.util import format_string
from src.flaskapp.db import coll
from src.flaskapp.schemas import (
    ensure_json,
    ensure_user_logged_in,
    ensure_feature_is_enabled,
)


def mark_team_complete(email):
    """reverse team completion status

       change team completion status:
        if it was incomplete, mark it complete
        if it was complete, mark it incomplete.

       Args:
           email: email of any team member

       Return:
            response object
       """
    email = email.strip().lower()
    team = coll("teams").find_one({"members": {"$all": [email]}})
    if not team:
        return {"message": "User not in a team"}, 401

    team_name = team["_id"]
    team_complete = team["complete"]
    team_size = len(team["members"])
    if team_complete is True and team_size <= 4:
        coll("teams").update_one({"_id": team_name}, {"$set": {"complete": False}})
        return {"message": "False"}, 200
    else:
        coll("teams").update_one({"_id": team_name}, {"$set": {"complete": True}})
        return {"message": "True"}, 200
