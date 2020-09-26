from flask import request

from src.flaskapp.db import coll
from src.flaskapp.schemas import (
    ensure_json,
    ensure_user_logged_in,
    ensure_feature_is_enabled,
)


def return_open_teams(search):
    """Find teams that are open for new members

       Give a list of teams that fulfills the requirement and also still open for new members,
       if search is empty, returns all open team.

       Args:
           search: json file filter for complete, desc, skills and prizes

       Return:
            list of open teams that pass the filter.
       """
    if search is None:
        available_teams = coll("teams").find({"complete": False})
        all_open_teams = []
        for x in available_teams:
            all_open_teams.append(x)
        if not all_open_teams:
            return {"message", "No open teams"}, 400
        return {"all_open_teams": all_open_teams}, 200
    else:
        search = search.strip.lower()
        available_teams = coll("teams").find(
            {
                "complete": False,
                "$or": [
                    {"desc": {"$regex": ".*" + search + ".*"}},
                    {"skills": {"$regex": ".*" + search + ".*"}},
                    {"prizes": {"$regex": ".*" + search + ".*"}},
                ],
            }
        )
        all_open_teams = []
        for x in available_teams:
            all_open_teams.append(x)
        if not all_open_teams:
            return {"message": "No open teams"}, 400
        return {"all_open_teams": all_open_teams}, 200
