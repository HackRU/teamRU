from flask import request

from src.flaskapp.lcs import call_auth_endpoint, get_name
from src.flaskapp.util import return_resp
from src.flaskapp.db import coll
from src.flaskapp.schemas import (
    ensure_json,
    ensure_user_logged_in,
    ensure_feature_is_enabled,
)


def get_team_profile(email):  # GET
    """get team information

       returns team information as text in json

       Args:
           email: email of any one of team member

       Return:
            Jsonified team info
       """

    team = coll("teams").find_one({"members": {"$all": [email]}})
    if not team:
        return return_resp(400, "Team Not found")
    else:
        members = team["members"]
        members_names = []
        for member in members:
            token = call_auth_endpoint()
            if token == 200:
                continue
            name = get_name(token, member)
            if name == 200:
                continue
            members_names.append(name)
            team.update({"names": members_names})
        return return_resp(200, team)

