from src.flaskapp.util import return_resp
from src.flaskapp.db import coll


def user_interested(email, team_name):  # POST
    """Adds this user to a team's interested list

    If an individual is interested in joining a team then he or she can be put into the interested section of a team

    Args:
        email: the email of the individual that is interested
        team_name: the name of the team that the individual is interested in

    Return:
        response object
    """
    user_in_a_team = coll("users").find_one({"_id": email, "hasateam": True})
    if user_in_a_team:
        return return_resp(403, "User in a team")
    team = coll("teams").find_one({"_id": team_name})
    if not team:
        return return_resp(402, "Invalid name")
    complete = coll("teams").find_one({"_id": team_name, "complete": True})
    if complete or len(team["members"]) >= 4:
        return return_resp(405, "Team complete")
    coll("teams").update_one({"_id": team_name}, {"$push": {"interested": email}})
    coll("users").update_one({"_id": email}, {"$push": {"potentialteams": team_name}})
    return return_resp(200, "Success")
