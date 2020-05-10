from app.util import call_validate_endpoint, return_resp, coll
from flask import request


def get_open_teams(email, token):
    email = email.strip().lower()
    if call_validate_endpoint(email, token) != 200:
        return return_resp(404, "Invalid request")
    else:
        if request.method == 'GET':
            data = request.get_json(silent=True)
            if not data or 'filter' not in data or not data['filter']:
                available_teams = coll("teams").find({"complete": False})
                all_open_teams = []
                for x in available_teams:
                    all_open_teams.append(x)
                if not all_open_teams:
                    return return_resp(400, "No open teams")
                return return_resp(200, all_open_teams)
            else:
                search = data['filter'].lower().strip()
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
