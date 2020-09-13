from src.flaskapp.db import coll


def user_leave(email):  # POST
    """the user leaves a team

    Removes the individual from the team

    Args:
        email: the email of the individual that wants to leave the team

    Return:
        response object
    """
    user_in_a_team = coll("users").find_one({"_id": email, "hasateam": True})
    if not user_in_a_team:
        return {"message": "User doesn't have a tram"}, 400
    team_name = coll("teams").find_one({"members": {"$all": [email]}}, {"_id"})["_id"]
    team_size = len(coll("teams").find_one({"_id": team_name})["members"])
    if team_size == 1:
        coll("teams").delete_one({"_id": team_name})
    else:
        coll("teams").update_one({"_id": team_name}, {"$pull": {"members": email}})
        coll("teams").update_one({"_id": team_name}, {"$set": {"complete": False}})
    coll("users").update_one({"_id": email}, {"$set": {"hasateam": False}})
    return {"message": "Success"}, 200
