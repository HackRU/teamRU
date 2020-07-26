from src.flaskapp.lcs import call_auth_endpoint, get_name
from src.flaskapp.util import return_resp, format_string
from src.flaskapp.db import coll
from src.flaskapp.schemas import (
    ensure_json,
    ensure_user_logged_in,
    ensure_feature_is_enabled,
)


def get_user_profile(email):  # GET
    user_profile = coll("users").find_one({"_id": email})
    if not user_profile:
        return return_resp(200, "User Not found")
    dir_token = call_auth_endpoint()
    if dir_token != 400:
        name = get_name(dir_token, email)
    else:
        name = ""
    user_profile.update({"name": name})
    return return_resp(200, user_profile)


def create_user_profile(email, **kwargs):  # POST
    # NOTE Originally skills was required for user to create profile
    # if not data or "skills" not in data or not data["skills"]: required
    #     return return_resp(400, "Required info not found")
    prizes = kwargs["prizes"]
    skills = kwargs["skills"]

    user_exists = coll("users").find_one({"_id": email})
    if user_exists:
        coll("users").update(
            {"_id": email}, {"$set": {"skills": skills, "prizes": prizes}}
        )
        return return_resp(200, "Successful update")
    else:
        coll("users").insert_one(
            {
                "_id": email,
                "skills": skills,
                "prizes": prizes,
                "hasateam": False,
                "potentialteams": [],
            }
        )
        return return_resp(201, "Profile created")
