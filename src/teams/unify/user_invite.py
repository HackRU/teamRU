from src.flaskapp.db import coll
from src.teams.unify.team_invite import team_invite


def user_invite(email, team1_id, user2_email):  # POST
    """Invite another team to join 1 person team (i.e. team1 -inviting -> user2)
    This endpoints allows users to find other team members using email

    #NOTE user_invite is dependent on team_invite

    Peforms checks to see if user2 is a valid user and whether user2's team is also valid
    then uses team_invite to carry out the invite

    Args:
        team1_id: the id of the team that is inviting user2
        user2_email: the email of the invitee

    Return:
        response object
    """

    user = coll("users").find_one({"_id": user2_email})
    print("HI")
    if not user:
        return {"message": f"User ({user2_email}) does not exist"}, 400
    team2_id = user["team_id"]
    if not team2_id:
        return {"message": f"User ({user2_email} does not have a team"}, 400

    team2 = coll("teams").find_one({"_id": team2_id})

    if not team2:
        return {"message": f"Team {team2_id} does not exist"}, 400

    if len(team2["members"]) > 1:
        return {"message": f"User ({user2_email}) already on a team with others"}, 400
    else:
        return team_invite(email, team1_id, team2_id)