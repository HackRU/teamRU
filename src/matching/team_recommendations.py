from src.flaskapp.db import coll
from src.flaskapp.util import aggregate_team_meta


def get_team_recommendations(email):  # GET
    """Finds recommendations of teams for this individual to join

    The current matching algorithms finds teams that are not full already by matching on prizes and skills.

    Args:
        email: the email of the individual that wants recommendations of teams to join

    Return:
        a list of recommended teams to join
    """

    user = coll("users").find_one({"_id": email})
    if not user:
        return {"message": "Invalid user"}, 403
    user_in_a_team = coll("users").find_one({"_id": email, "hasateam": True})
    if user_in_a_team:
        return {"message": "User in a team"}, 400
    # basic info about users
    if "skills" not in user or not user["skills"]:
        skills = []
    else:
        skills = user["skills"]
    if "interests" not in user or not user["interests"]:
        interests = []
    else:
        interests = user["interests"]
    if "prizes" not in user or not user["prizes"]:
        prizes = []
    else:
        prizes = user["prizes"]
    if "seriousness" not in user or not user["seriousness"]:
        seriousness = 0
    else:
        seriousness = user["seriousness"]

    names = set()
    matches = []

    # match for skill
    needed_skills = []
    # judging if the user if frontend or backend
    frontend_languages = ["html", "css", "javascript", "php", "typscript"]
    backend_languages = ["java", "php", "ruby", "python", "c", "c++", "sql", "node.js"]
    front_or_back = "none"
    for original_skill in skills:
        original_skill = original_skill.lower()
        if original_skill in frontend_languages:
            if front_or_back == "back":
                front_or_back = "none"
                break
            else:
                front_or_back = "front"

        if original_skill in backend_languages:
            if front_or_back == "front":
                front_or_back = "none"
                break
            else:
                front_or_back = "front"
    # give backend suggestions if only know frontend, vice versa
    if front_or_back == "front":
        needed_skills.append(frontend_languages)
    if front_or_back == "back":
        needed_skills.append(backend_languages)

    for skill in needed_skills:
        # collection of all the team's skills
        complementary_skills_match = coll("teams").aggregate(
            [{"$match": {"complete": False, "skills": {"$all": [skill]}}}]
        )
        # collections of all the team's interests
        if not complementary_skills_match:
            continue
        for match in complementary_skills_match:
            if match['_id'] not in names:
                names.add(match['_id'])
                matches.append(match)

    # add base on interests
    # AR/VR, BlockChain, Communications, CyberSecurity, DevOps, Fintech, Gaming,
    # Healthcare, IoT, LifeHacks, ML/AI, Music, Productivity, Social Good, Voice Skills

    # finding team with listed interests, if too much matches, find from teams in the matches
    if len(matches) > 50:
        for match in matches:
            if len(matches) <= 50:
                break
            team_interests = match["meta"]["interests"]
            # team has no common skill
            if len(list(set(interests).intersection(set(team_interests)))) == 0:
                matches.remove(match)
                names.remove(match["_id"])
    else:
        for interest in interests:
            match = coll("teams").aggregate([{"$match": {"complete": False, "meta.interest": {"$all": [interest]}}}])
            if not match:
                continue
            for m in match:
                if m["_id"] not in names:
                    names.add(m["_id"])
                    matches.append(m)

    # add suggestions base on prize
    for prize in prizes:
        match = coll("teams").aggregate([{"$match": {"complete": False, "prizes": {"$all": [prize]}}}])
        if not match:
            continue
        for m in match:
            if m["_id"] not in names:
                names.add(m["_id"])
                matches.append(m)

    # if there are too many matches, reduce it base on seriousness
    if len(matches) > 20:
        for team in matches:
            if (abs(team["seriousness"] - seriousness)) > 2:
                matches.remove(team)
                names.remove(team["_id"])

    # return
    if not matches:
        return {"message": "No recommendations found"}, 404

    for team in matches:
        team["team_id"] = team.pop("_id")
    return {"matches": matches}, 200

