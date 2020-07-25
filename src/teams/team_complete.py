from flask import request

from src.flaskapp.util import return_resp
from src.flaskapp.db import coll
from src.flaskapp.schemas import ensure_json, ensure_user_logged_in, ensure_feature_is_enabled

@ensure_json()
@ensure_user_logged_in()
@ensure_feature_is_enabled("team complete")
def mark_team_complete():
    if request.method == 'POST':
        data = request.get_json(silent=True)
        email = data['user_email']
        email = email.strip().lower()
        team = coll("teams").find_one({"members": {"$all": [email]}})
        if not team:
            return return_resp(401, "User not in a team")
        team_name = team['_id']
        team_complete = team['complete']
        if team_complete is True:
            coll("teams").update_one({"_id": team_name}, {"$set": {"complete": False}})
            return return_resp(200, "False")
        else:
            coll("teams").update_one({"_id": team_name}, {"$set": {"complete": True}})
            return return_resp(200, "True")
