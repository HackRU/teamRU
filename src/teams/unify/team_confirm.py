from src.flaskapp.db import coll
from src.flaskapp.util import aggregate_team_meta

# same issue here,
def team_confirm(team1_name, team2_name):  # if request.method == 'POST'
    """Confirming an invitation from a team (i.e. team1 -confirms-> team2)

       Performs checks to see if the merging can be carried out still (checks include: 1) new team size is not > 4 2) no rescinds or rejects beforehand which would have nullified the invite) 
       
       If checks pass then team2 is merged with team1 by adding team2's member(s) into team1's member list and setting team1 to complete if the new team size is 4

       Args:
           team1_name: name of the team that is confirming the invite (invitee)
           team2_name: name of the team that sent the invite (inviter)

       Return:
            response object
       """
    # team_name = coll("teams").find_one({"members": {"$all": [email]}}, {"_id"})["_id"]
    # team = coll("teams").find_one({"_id": team_name})
    # team_members = team["members"]
    team1 = coll("teams").find_one({"_id": team1_name})
    team2 = coll("teams").find_one({"_id": team2_name})

    # complete = coll("teams").find_one({"_id": team_name, "complete": True})
    if not team1 or not team2:
        return {"message": "Invalid name"}, 402
    if email not in team1["members"]:
        return {"message": f"User not in team {team1_name}"}, 403
    if (new_length := len(team1["members"]) + len(team2["members"])) > 4:
        return {"message": "Team size will be greater than 4"}, 403
    if team1["complete"] or team2["complete"]:
        return {"message": "Team Complete"}, 405
    if not (
        team1_name in team2["outgoing_inv"] and team2_name in team1["incoming_inv"]
    ):
        return (
            {"message": "invite no longer valid"},
            402,
        )  # FIXME not sure about the error code

    # coll("users").update_one({"_id": hacker}, {"$set": {"hasateam": True}})
    # coll("users").update_one({"_id": hacker}, {"$pull": {"potentialteams": team_name}})

    # NOTE So we can do merging of the two teams (documents)however we want (this is just an example) currently the other team is being deleted but we should really archive it for futuring training purposes for our ML model
    coll("teams").update_one(
        {"_id": team2_name},
        {
            "$push": {"members": {"$each": team1["members"]}},
            "$pull": {"outgoing_inv": team1_name},
            "$set": {"complete": new_length == 4},
            "$set": {"meta": aggregate_team_meta(team1["members"] + team2["members"])},
        },
    )
    coll("teams").delete_one({"_id": team1_name})
    # coll("teams").update_one({"_id": team2_name}, {"$pull": {"interested": hacker}})
    return {"message": "Success"}, 200
