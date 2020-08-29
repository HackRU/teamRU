from src.flaskapp.lcs import call_auth_endpoint, get_name
from src.flaskapp.util import format_string
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
        return {"message": "User Not found"}, 200
    dir_token = call_auth_endpoint()
    if dir_token != 400:
        name = get_name(dir_token, email)
    else:
        name = ""
    user_profile.update({"name": name})
    return user_profile, 200


def get_user_profiles(args):  # GET
    """Endpoint to get multiple user profiles at once

    Args (Optional):
    1. limit - int - number of user profiles to return. Default value = 0 which will return everything
    2. hasateam - bool - returns user that are in a team or not Default value = none which returns both

    Returns a list of users

    """
    limit = args.get("limit", type=int) if args.get("limit") else 0
    hasateam = args.get("hasateam")

    if hasateam:
        users = list(
            coll("users")
            .find({"hasateam": hasateam.lower() == "true"})
            .limit(
                limit
            )  # NOTE checks if the string value of hasateam is equal to "true" because HTTP protocol only passes strings
        )
    else:
        users = list(coll("users").find({}).limit(limit))

    return {"user_profiles": users}, 200


def create_user_profile(email, **kwargs):  # POST
    # NOTE Originally skills was required for user to create profile
    # if not data or "skills" not in data or not data["skills"]: required
    #     return {"message": "Required info not found"}, 400

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
        return {"message", "User already exists"}, 401

    coll("users").insert_one(
        {
            "_id": email,
            "skills": skills,
            "prizes": prizes,
            "hasateam": False,
            "potentialteams": [],
        }
    )
    return {"message": "Profile created"}, 201


def update_user_profile(email, **kwargs):  # PUT
    prizes = kwargs["prizes"]
    skills = kwargs["skills"]

    user_exists = coll("users").find_one({"_id": email})
    if not user_exists:
        return {"message": "User does not exist"}, 404

    coll("users").update({"_id": email}, {"$set": {"skills": skills, "prizes": prizes}})
    return {"message": "Successful update"}, 200
