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
        return {"message": "No recommendations found"}, 400
    if "prizes" not in user or not user["prizes"]:
        prizes = []
    else:
        prizes = user["prizes"]
        skills = user["skills"]
        names = set()

    matches = []
    for skill in skills:
        complementary_skills_match = coll("teams").aggregate(
            [{"$match": {"complete": False, "partnerskills": {"$all": [skill]}}}]
        )
        interests_match = coll("teams").aggregate(
            [{"$match": {"complete": False, "interested": {"$all": [skill]}}}]
        )

        if not complementary_skills_match or interests_match:
            continue
        for this_interest in interests_match:
            if this_interest["_id"] not in names:
                names.add(this_interest["_id"])
                matches.append(this_interest)


        frontend_languages = ["HTML", "CSS", "JavaScript"]
        backend_languages = ["Java", "PHP", "Ruby", "Python", "c", "c++"]


        front_or_back = "none"
        for original_skill in complementary_skills_match:
            if original_skill in frontend_languages:
                front_or_back = "front"
            if original_skill in backend_languages:
                front_or_back = "back"

        if front_or_back == "front":
            complementary_skills_match.append( frontend_languages )
        if front_or_back == "back":
            complementary_skills_match.append(backend_languages)

        for this_skill in complementary_skills_match:
            if this_skill["_id"] not in names:
                names.add(this_interest["_id"])
                matches.append(this_interest)

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
    return {"matches": matches}, 200
