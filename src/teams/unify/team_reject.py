from src.flaskapp.db import coll


def team_reject(email, team1_name, team2_name):  # POST
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
        return {"message": "Invalid team name(s)"}, 404

    if email not in team1["members"]:
        return {"message": f"User not in team {team1_name}"}, 403

    if team1_name not in team2["outgoing_inv"] or team2_name not in team1["incoming_inv"]:
        return {"message": "No invite to reject"}, 404

    coll("teams").update_one(
        {"_id": team1_name}, {"$pull": {"incoming_inv": team2_name}}
    )
    coll("teams").update_one(
        {"_id": team2_name}, {"$pull": {"outgoing_inv": team1_name}}
    )
    return {"message": "Success"}, 200
