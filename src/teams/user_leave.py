from src.flaskapp.db import coll
from src.flaskapp.util import aggregate_team_meta


def user_leave(email, team_id):  # POST
    """the user leaves a team

    Removes the individual from the team

    Args:
        email: the email of the individual that wants to leave the team

    Return:
        response object
    """
    team = coll("teams").find_one({"_id": team_id})
    if not team:
        return {"message": "Team does not exist"}, 400

    if email not in team["members"]:
        return {"message": f'User not in team "{team_id}"'}, 403

    team_size = len(team["members"])
    if team_size == 1:
        # coll("teams").delete_one({"_id": team["_id"]})

        # Maybe also turn this team into complete?
        return {"message": "A team must have one member"}, 400
    else:
        coll("teams").update_one(
            {"_id": team["_id"]},
            {
                "$pull": {"members": email},
                "$set": {"complete": False},
                "$set": {
                    "meta": aggregate_team_meta(
                        [member for member in team["members"] if member != email],
                    )
                },
            },
        )

    # Reset the User
    coll("users").update_one(
        {"_id": email}, {"$set": {"hasateam": False, "team_id": ""}}
    )

    return {"message": "Success"}, 200
