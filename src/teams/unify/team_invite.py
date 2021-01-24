from src.flaskapp.db import coll
from src.flaskapp.mailgun import send_email


def team_invite(email, team1_id, team2_id):  # POST
    """Invite another team to join your team (i.e. team1 -inviting-> team2)

    Performs checks to see if these two team can merge then adds team2 to team1's outgoing_inv
    list and adds team1 to team2's incoming_inv list

    Args:
        team1_id: the id of the team that is interested in team2 (inviter)
        team2_id: the id of the team that catches the interest of team1 (invitee)

    Return:
        response object
    """
    team1 = coll("teams").find_one({"_id": team1_id})
    team2 = coll("teams").find_one({"_id": team2_id})

    if not team1 or not team2:
        return ({"message": "Invalid team id(s)"}, 404)

    if email not in team1["members"]:
        return ({"message": f"User not in team {team1_id}"}, 403)

    if team1_id == team2_id:  # check to see if you are sending invite to yourself
        return ({"message": "Cannot invite your own team"}, 400)

    if (
        team1_id in team2["incoming_inv"]
    ):  # (team2_id in team1["outgoing_inv"] will also work) check to see if you are sending a duplicate invite
        return ({"message": "Cannot have duplicate invite"}, 400)

    if len(team1["members"]) + len(team2["members"]) > 4:
        return ({"message": "Team size will be greater than 4"}, 409)

    if team1["complete"] or team2["complete"]:
        return ({"message": "Team already complete "}, 409)

    coll("teams").update_one({"_id": team1_id}, {"$push": {"outgoing_inv": team2_id}})
    coll("teams").update_one({"_id": team2_id}, {"$push": {"incoming_inv": team1_id}})
    send_email(
        to=team2["members"],
        subject="Pending TeamRU Invite",
        body="Go to https://hackru.org/ to accept the invite",
    )
    return ({"message": "Success"}, 200)
