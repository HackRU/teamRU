from flask import request

from src.flaskapp.lcs import call_auth_endpoint, get_name
from src.flaskapp.util import format_string, return_resp
from src.flaskapp.db import coll
from src.flaskapp.schemas import (
    ensure_json,
    ensure_user_logged_in,
    ensure_feature_is_enabled,
)


def add_member(email, partner_email):  # if request.method == 'POST'
    """invite new member

       Send invite to a potential teammate, from a member.

       Args:
           email: the email of the individual already in the the team
           partner_email: email of the member being added

       Return:
            response object
       """
    dir_token = call_auth_endpoint()
    if dir_token == 400:
        return return_resp(401, "auth endpoint failed")
    if get_name(dir_token, partner_email) == 400:
        return return_resp(402, "Partner doesn't have a hackRU account")
    team = coll("teams").find_one({"members": {"$all": [email]}})
    if not team:
        return return_resp(405, "User not in a team")
    team_name = team["_id"]
    team_size = len(team["members"])
    team_full = coll("teams").find_one({"_id": team_name, "complete": True})
    if team_full or team_size >= 4:
        return return_resp(403, "Team complete")
    user_exist = coll("users").find_one({"_id": partner_email})
    if not user_exist:
        coll("users").insert(
            {"_id": partner_email, "hasateam": True, "skills": [], "prizes": []}
        )
        coll("teams").update_one(
            {"_id": team_name}, {"$push": {"members": partner_email}}
        )
        return return_resp(200, "Success")
    else:
        partner_in_a_team = coll("users").find_one(
            {"_id": partner_email, "hasateam": True}
        )
        if not partner_in_a_team:
            coll("users").update_one(
                {"_id": partner_email}, {"$set": {"hasateam": True}}
            )
            coll("teams").update_one(
                {"_id": team_name}, {"$push": {"members": partner_email}}
            )
            if team_size == 4:
                coll("teams").update_one(
                    {"_id": team_name}, {"$set": {"complete": True}}
                )
            return return_resp(200, "Success")
        else:
            return return_resp(406, "Partner in a team")
