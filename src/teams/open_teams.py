from flask import request

from src.flaskapp.util import return_resp
from src.flaskapp.db import coll
from src.flaskapp.schemas import ensure_json, ensure_user_logged_in, ensure_feature_is_enabled

def return_open_teams(search):
    if search is None:
        available_teams = coll("teams").find({"complete": False})
        all_open_teams = []
        for x in available_teams:
            all_open_teams.append(x)
        if not all_open_teams:
            return return_resp(400, "No open teams")
        return return_resp(200, all_open_teams)
    else:
        search = search.strip.lower()
        available_teams = coll("teams").find({"complete": False, "$or": [
            {"desc": {"$regex": ".*" + search + ".*"}},
            {"partnerskills": {"$regex": ".*" + search + ".*"}},
            {"prizes": {"$regex": ".*" + search + ".*"}}
        ]
                                              })
        all_open_teams = []
        for x in available_teams:
            all_open_teams.append(x)
        if not all_open_teams:
            return return_resp(400, "No open teams")
        return return_resp(200, all_open_teams)


@ensure_json()
@ensure_user_logged_in()
@ensure_feature_is_enabled("open teams")
def get_open_teams():
    if request.method == 'GET':
        data = request.get_json(silent=True)
        if 'filter' not in data or not data['filter']:
            search = None
        else:
            search = data['filter']
        return return_open_teams(search)
