from src.flaskapp.util import {"message": 
from src.flaskapp.db import coll


def get_team_recommendations(email):  # GET
    """Finds recommendations of teams for this individual to join

    The current matching algorithms finds teams that are not full already by matching on prizes and skills.

    Args:
        email: the email of the individual that wants recommendations of teams to join

    Return:
        a list of recommmended teams to join

    """
    user = coll("users").find_one({"_id": email})
    if not user:
        return {"message": "Invalid user"}, 403
    user_in_a_team = coll("users").find_one({"_id": email, "hasateam": True})
    if user_in_a_team:
        return {"message": "User in a team"}, 402
    if "skills" not in user or not user["skills"]:
        return {"message":"No recommendations found"}, 400
    if "prizes" not in user or not user["prizes"]:
        prizes = []
    else:
        prizes = user["prizes"]
    skills = user["skills"]
    names = set()
    matches = []
    for skill in skills:
        match = coll("teams").aggregate(
            [{"$match": {"complete": False, "partnerskills": {"$all": [skill]}}}]
        )
        if not match:
            continue
        for m in match:
            if m["_id"] not in names:
                names.add(m["_id"])
                matches.append(m)
    for prize in prizes:
        match = coll("teams").aggregate(
            [{"$match": {"complete": False, "prizes": {"$all": [prize]}}}]
        )
        if not match:
            continue
        for m in match:
            if m["_id"] not in names:
                names.add(m["_id"])
                matches.append(m)
    if not matches:
        return {"message": "No recommendations found"}, 400
    return {"matches":matches}, 200}

