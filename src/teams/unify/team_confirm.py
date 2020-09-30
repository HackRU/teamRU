from src.flaskapp.db import coll
from src.flaskapp.util import aggregate_team_meta


def team_confirm(email, team1_name, team2_name):  # if request.method == 'POST'
    """Confirming an invitation from a team (i.e. team1 -confirms-> team2)

    team1 is the team which is receiving and confirming the invite
    team2 is the team which made the original invite

    Performs checks to see if the merging can be carried out still (checks include: 1) new team
    size is not > 4 2) no rescinds or rejects beforehand which would have nullified the invite)

    If checks pass then team1 (confirming team) is merged with team2 (original team) by adding 
    team1's member(s) into team2's member list and setting team2 to complete if the new team size is 4

    Args:
        team1_name: name of the team that is confirming the invite (invitee)
        team2_name: name of the team that sent the invite (inviter)

    Return:
         response object
    """
    team1 = coll("teams").find_one({"_id": team1_name})
    team2 = coll("teams").find_one({"_id": team2_name})

    if not team1 or not team2:
        return {"message": "Invalid team name(s)"}, 404

    if email not in team1["members"]:
        return {"message": f"User not in team {team1_name}"}, 403

    new_length = len(team1["members"]) + len(team2["members"])
    if new_length > 4:
        return {"message": "Team size will be greater than 4"}, 409

    if team1["complete"] or team2["complete"]:
        return {"message": "Team complete"}, 409

    if team1_name not in team2["outgoing_inv"] and team2_name not in team1["incoming_inv"]:
        return {"message": "Invite no longer exists"}, 404

    # NOTE So we can do merging of the two teams (documents) however we want (this is just an example)
    # currently the other team is being deleted but we should really archive it for futuring training
    # purposes for our ML model
    coll("teams").update_one(
        {"_id": team2_name},
        {
            "$push": {"members": {"$each": team1["members"]}},
            "$pull": {"outgoing_inv": team1_name},
            "$set": {
                "complete": new_length == 4,
                "meta": aggregate_team_meta(team1["members"] + team2["members"]),
            },
        },
    )
    coll("teams").delete_one({"_id": team1_name})
    return {"message": "Success"}, 200
