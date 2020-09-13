from src.flaskapp.db import coll


def team_rescind(team1_name, team2_name):  # POST
    """rescind an invite (i.e. team1 -rescind-> team2)

    Removes team2 from team1 outgoing_inv and removes team1 from team2's incoming_inv

    Args:
        team1_name: name of the team that is rescinding the invite (i.e. the team that sent the invite)
        team2_name: name of the team that is rescinded (i.e. the invitee)
    
    Returns:
        response object
    """
    team1 = coll("teams").find_one({"_id": team1_name})
    team2 = coll("teams").find_one({"_id": team2_name})
    if not team1 or not team2:
        return {"message": "Invalid name"}, 402
    # FIXME Don't know if this is going to be an issue but this doesn't return an error if the endpoint is rejecting an invite that doesn't exist.
    coll("teams").update_one(
        {"_id": team1_name}, {"$pull": {"outgoing_inv": team2_name}}
    )
    coll("teams").update_one(
        {"_id": team2_name}, {"$pull": {"incoming_inv": team1_name}}
    )
    return {"message": "Success"}, 200
