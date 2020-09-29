from src.flaskapp.db import coll


def team_rescind(email, team1_name, team2_name):  # POST
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
        return {"message": "Invalid team name(s)"}, 404

    if email not in team1["members"]:
        return {"message": f"User not in team {team1_name}"}, 403

    if team1_name not in team2["incoming_inv"] or team2_name not in team1["outgoing_inv"]:
        return {"message": "No invite to rescind"}, 404

    coll("teams").update_one(
        {"_id": team1_name}, {"$pull": {"outgoing_inv": team2_name}}
    )
    coll("teams").update_one(
        {"_id": team2_name}, {"$pull": {"incoming_inv": team1_name}}
    )
    return {"message": "Success"}, 200
