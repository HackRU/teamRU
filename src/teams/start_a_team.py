from flask import request

from src.flaskapp.util import format_string, return_resp
from src.flaskapp.db import coll
from src.flaskapp.schemas import (
    ensure_json,
    ensure_user_logged_in,
    ensure_feature_is_enabled,
)


@ensure_json()
@ensure_user_logged_in()
@ensure_feature_is_enabled("start a team")
def create_team():
    if request.method == "POST":
        data = request.get_json(silent=True)
        email = data["user_email"]
        email = format_string(email)
        if (
            not data
            or "name" not in data
            or "desc" not in data
            or "skills" not in data
            or not data["name"]
            or not data["desc"]
            or not data["skills"]
        ):
            return {"statusCode": 400, "body": "Required info not found"}
        team_name = format_string(data["name"])
        team_desc = format_string(data["desc"])
        partner_skills = data["skills"]
        formatted_skills = format_string(partner_skills)
        formatted_prizes = []
        if "prizes" in data:
            prizes = data["prizes"]
            formatted_prizes = format_string(prizes)
        team_exist = coll("teams").find_one({"_id": str(team_name)})
        user_exists = coll("users").find_one({"_id": email})
        if not user_exists:
            return return_resp(403, "Invalid user")
        if team_exist:
            return return_resp(401, "Invalid name")
        else:
            user_in_a_team = coll("users").find_one({"_id": email, "hasateam": True})
            if user_in_a_team:
                return return_resp(402, "User in a team")
            else:
                coll("users").update_one({"_id": email}, {"$set": {"hasateam": True}})
                coll("teams").insert(
                    {
                        "_id": team_name,
                        "members": [email],
                        "desc": team_desc,
                        "partnerskills": formatted_skills,
                        "prizes": formatted_prizes,
                        "complete": False,
                        "interested": [],
                    }
                )
                return return_resp(200, "Success")
