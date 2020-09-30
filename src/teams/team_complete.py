from src.flaskapp.db import coll


def team_complete(email, team_id):
    """reverse team completion status

    change team completion status:
    if it was incomplete, mark it complete
    if it was complete, mark it incomplete.

    Args:
        email: email of any team member

    Return:
        response object
    """
    team = coll("teams").find_one({"_id": team_id})
    if not team:
        return {"message": "Team does not exist"}, 400

    if email not in team["members"]:
        return {"message": f'User not in team "{team_id}"'}, 403

    team_size = len(team["members"])
    if team["complete"] and team_size <= 4:
        coll("teams").update_one({"_id": team_id}, {"$set": {"complete": False}})
        return {"message": "False"}, 200
    else:
        coll("teams").update_one({"_id": team_id}, {"$set": {"complete": True}})
        return {"message": "True"}, 200
