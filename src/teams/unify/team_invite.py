from src.flaskapp.db import coll


def team_invite(email, team1_name, team2_name):  # POST
    """Invite another team to join your team (i.e. team1 -inviting-> team2)

    Performs checks to see if these two team can merge then adds team2 to team1's outgoing_inv
    list and adds team1 to team2's incoming_inv list

    Args:
        team1_name: the name of the team that is interested in team2 (inviter)
        team2_name: the name of the team that catches the interest of team1 (invitee)

    Return:
        response object
    """
    # user_in_a_team = coll("users").find_one({"_id": email, "hasateam": True})
    # if user_in_a_team:
    #     return {"message": "User in a team"}, 403

    team1 = coll("teams").find_one({"_id": team1_name})
    team2 = coll("teams").find_one({"_id": team2_name})

    if not team1 or not team2:
        return {"message": "Invalid name"}, 402
    if email not in team1["members"]:
        return {"message": f"User not in team {team1_name}"}, 403
    if len(team1["members"]) + len(team2["members"]) > 4:
        return {"message": "Team size will be greater than 4"}, 403
    if team1["complete"] or team2["complete"]:
        return {"message": "Team already complete "}, 405

    # complete = coll("teams").find_one({"_id": team_name, "complete": True})
    # if complete or len(team["members"]) >= 4:
    #     return {"message": "Team complete"}, 405

    coll("teams").update_one(
        {"_id": team1_name}, {"$push": {"outgoing_inv": team2_name}}
    )
    coll("teams").update_one(
        {"_id": team2_name}, {"$push": {"incoming_inv": team1_name}}
    )
    return {"message": "Success"}, 200
