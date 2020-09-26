from src.flaskapp.db import coll
from src.flaskapp.util import aggregate_team_meta


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
        return {"message": "User doesn't have a team"}, 400
    team = coll("teams").find_one({"members": {"$all": [email]}})
    team_size = team["members"]
    if team_size == 1:
        coll("teams").delete_one({"_id": team["_id"]})
    else:
        coll("teams").update_one(
            {"_id": team["_id"]},
            {"$pull": {"members": email}, "$set": {"complete": False}},
            {
                "$set": {
                    "meta": aggregate_team_meta(
                        [member for member in team["members"] if not (member == email)],
                    )
                }
            },
        )
    coll("users").update_one({"_id": email}, {"$set": {"hasateam": False}})
    return {"message": "Success"}, 200
