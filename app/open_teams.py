from app.util import call_validate_endpoint, return_resp, coll, validate_feature_is_enabled
from flask import request


def return_open_teams(email, token, search):
    email = email.strip().lower()
    if call_validate_endpoint(email, token) != 200:
        return return_resp(404, "Invalid request")
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


@validate_feature_is_enabled("open teams")
def get_open_teams():
    if request.method == 'GET':
        data = request.get_json(silent=True)
        if not data or 'user_email' not in data or not data['user_email'] or 'token' not in data or not data['token']:
            return return_resp(408, "Missing email or token")
        email = data['user_email']
        token = data['token']
        if 'filter' not in data or not data['filter']:
            search = None
        else:
            search = data['filter']
        return return_open_teams(email, token, search)
