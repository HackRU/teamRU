from flask import request

from src.flaskapp.util import format_string, return_resp
from src.flaskapp.db import coll
from src.flaskapp.schemas import (
    ensure_json,
    ensure_user_logged_in,
    ensure_feature_is_enabled,
)


def mark_team_complete(team):
    """reverse team completion status

       change team completion status:
        if it was incomplete, mark it complete
        if it was complete, mark it incomplete.

       Args:
           team:team object

       Return:
            response object
       """
    # TODO: Check size of team before allowing user actions (if team size is 4, don't let them mark open)
    team_name = team["_id"]
    team_complete = team["complete"]
    if team_complete is True:
        coll("teams").update_one({"_id": team_name}, {"$set": {"complete": False}})
        return return_resp(200, "False")
    else:
        coll("teams").update_one({"_id": team_name}, {"$set": {"complete": True}})
        return return_resp(200, "True")
