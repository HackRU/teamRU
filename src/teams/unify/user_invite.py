from src.flaskapp.db import coll
from src.teams.unify.team_invite import team_invite


def user_invite(email, team1_id, user2_email):  # POST
    """"""

    user = coll("users").find_one({"_id": user2_email})
    print("HI")
    if not user:
        return {"message": f"User ({user2_email}) does not exist"}, 400
    team2_id = user["team_id"]
    if not team2_id:
        return {"message": f"User ({user2_email} does not have a team"}, 400

    team2 = coll("teams").find_one({"_id": team2_id})

    if len(team2["members"]) > 1:
        return {"message": f"User ({user2_email}) already on a team with others"}, 400
    else:
        return team_invite(email, team1_id, team2_id)