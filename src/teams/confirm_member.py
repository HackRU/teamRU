from flask import request

from src.flaskapp.util import format_string, return_resp
from src.flaskapp.db import coll
from src.flaskapp.schemas import (
    ensure_json,
    ensure_user_logged_in,
    ensure_feature_is_enabled,
)


# same issue here,
def confirm(email, hacker):  # if request.method == 'POST'
    """confirm new member

       team member accept a new member's request to join.

       Args:
           email: the email of the individual already in the the team
           hacker: user id for new member

       Return:
            response object
       """
    team_name = coll("teams").find_one({"members": {"$all": [email]}}, {"_id"})["_id"]
    team = coll("teams").find_one({"_id": team_name})
    team_members = team["members"]
    complete = coll("teams").find_one({"_id": team_name, "complete": True})
    if len(team_members) >= 4 or complete:
        return return_resp(402, "Team Complete")
    coll("users").update_one({"_id": hacker}, {"$set": {"hasateam": True}})
    coll("users").update_one({"_id": hacker}, {"$pull": {"potentialteams": team_name}})
    coll("teams").update_one({"_id": team_name}, {"$push": {"members": hacker}})
    coll("teams").update_one({"_id": team_name}, {"$pull": {"interested": hacker}})
    return return_resp(200, "Success")
