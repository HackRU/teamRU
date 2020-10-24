from src.flaskapp.db import coll


def get_user_profile(email):  # GET
    """Get user profile

    Fetches from the user collection by using the user's email as key.

    Args:
        User's email (str)

    Returns:
        User profile object (dict)
    """
    # NOTE: This method previously called LCS with director credentials in order to retrieve the user's name
    # We will update TeamRU to store names along with our user objects, saving the need to call LCS again
    user_profile = coll("users").find_one({"_id": email})
    if not user_profile:
        return {"message": "User not found"}, 404
    user_profile["user_id"] = user_profile.pop("_id")
    return user_profile, 200


def get_user_profiles(args):  # GET
    """Endpoint to get multiple user profiles at once

    Args (Optional):
    1. limit (int) - number of user profiles to return. Default value = 0 which will return everything
    2. hasateam (bool) - returns user that are in a team or not Default value = none which returns both

    Returns a list of users
    """
    limit = args.get("limit", type=int) if args.get("limit") else 0
    # NOTE checks if the string value of hasateam is equal to "true" because HTTP protocol only passes strings
    hasateam = args.get("hasateam", "").lower() == "true"

    if hasateam:
        users = list(coll("users").find({"hasateam": hasateam}).limit(limit))
    else:
        users = list(coll("users").find({}).limit(limit))

    for user in users:
        user["user_id"] = user.pop("_id")
    return {"user_profiles": users}, 200


def create_user_profile(email, **kwargs):  # POST
    """Create user profile

    Creates a new user profile from the user email, skills, prizes, and other fields.

    Args:
        1. User's email (str)
        2. skills (list of str) - optional
        3. prizes (list of str) - optional
        4. bio (str) - optional
        5. github (str) - optional
        6. interests (list of str) - optional (AR/VR, BlockChain, Communications, CyberSecurity,
            DevOps, Fintech, Gaming, Healthcare, IoT, LifeHacks, ML/AI, Music, Productivity,
            Social Good, Voice Skills)
        7. seriousness (enum {i.e. int - 1-5}) - optional | default value is 3 (neutral)

    Returns:
        User profile object (dict)
    """
    user_exists = coll("users").find_one({"_id": email})

    if user_exists:
        return {"message": "User already exists"}, 400

    # NOTE Doesn't make sense for a person to have prizes only a team should have this
    coll("users").insert_one(
        {
            "_id": email,
            "skills": kwargs["skills"],
            "prizes": kwargs["prizes"],
            "bio": kwargs["bio"],
            "github": kwargs["github"],
            "interests": kwargs["interests"],
            "seriousness": kwargs["seriousness"],
            "team_id": "",
            "hasateam": False,
        }
    )
    return {"message": "User profile successfully created"}, 201


def update_user_profile(email, **kwargs):  # PUT
    """Update user profile

    Update a user profile with new parameters.

    Args:
        1. user's email (str)
        2. skills (list of str) - optional
        3. prizes (list of str) - optional
        4. bio (str) - optional
        5. github (str) - optional

    Returns:
        Status of update (dict)
    """
    user = coll("users").find_one({"_id": email})
    if not user:
        return {"message": "User not found"}, 404

    coll("users").update_one({"_id": email}, {"$set": kwargs})

    return {"message": "User profile successfully updated"}, 200
