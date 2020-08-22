from src.flaskapp.lcs import call_auth_endpoint, get_name
from src.flaskapp.util import return_resp, format_string
from src.flaskapp.db import coll


def get_user_profile(email):  # GET
    """Gets user's profile

    Fetches from the user collection by using the user's email as key

    Args:
        User's email 
    
    Returns:
        an user profile object
    """
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

    """Creates an user profile

    Creates a new user profile from the user email, skills, and prizes. If the user does exist then we update the profile with the new parameters

    Args:
        1. User's email
        2. Skills (optional)
        3. Prizes (optional)

    Returns:
        response object
    """

    user_exists = coll("users").find_one({"_id": email})
    prizes = kwargs["prizes"] if kwargs["prizes"] else user_exists["prizes"]
    skills = kwargs["skills"] if kwargs["skills"] else user_exists["skills"]
    if user_exists:
        return return_resp(409, "User already exists")

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


def update_user_profile(email, **kwargs):  # PUT
    prizes = kwargs["prizes"]
    skills = kwargs["skills"]

    user_exists = coll("users").find_one({"_id": email})
    if not user_exists:
        return return_resp(404, "User does not exist")

    coll("users").update({"_id": email}, {"$set": {"skills": skills, "prizes": prizes}})
    return return_resp(200, "Successful update")
