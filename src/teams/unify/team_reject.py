from src.flaskapp.db import coll


def team_reject(team1_name, team2_name):  # POST
    """rejecting an invite (i.e. team1 -reject-> team2 (rejecting an invite)

    Removes team2 from team1's incoming_inv list and removes team1 from team2's outgoing_inv list

    Args:
        team1_name: name of the team that is doing the reject
        team2_name: name of the team that sent the invite

    Return:
        response object
    """
    team1 = coll("teams").find_one({"_id": team1_name})
    team2 = coll("teams").find_one({"_id": team2_name})
    if not team1 or not team2:
        return {"message": "Invalid name"}, 402
    # FIXME Don't know if this is going to be an issue but this doesn't return an error if the endpoint is rejecting an invite that doesn't exist.
    coll("teams").update_one(
        {"_id": team1_name}, {"$pull": {"incoming_inv": team2_name}}
    )
    coll("teams").update_one(
        {"_id": team2_name}, {"$pull": {"outgoing_inv": team1_name}}
    )
    return {"message": "Success"}, 200

