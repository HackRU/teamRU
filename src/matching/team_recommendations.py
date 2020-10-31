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
        return {"message": "Invalid user"},

    if user["hasateam"]:
        return {"message": "User in a team"}, 400
    # basic info about users
    skills = user["skills"]
    interests = user["interests"]
    prizes = user["prizes"]
    seriousness = user["seriousness"]

    names = set()
    matches = []

    # match for skill
    needed_skills = []

    frontend_languages = set(["html", "css", "javascript", "php", "typscript"])
    backend_languages = set(["java", "php", "ruby", "python", "c", "c++", "sql", "node.js"])
    # judging if the user if frontend or backend, and give backend suggestions if only know frontend, vice versa
    skill_set = set(skills)
    front_num = len(skill_set.intersection(skills))
    back_num = len(skill_set.intersection(skills))

    if front_num > (back_num * 5/8):
        if back_num < 3:
            needed_skills.append(backend_languages)
    else:
        if front_num < 3:
            needed_skills.append(frontend_languages)
    if len(needed_skills):
        needed_skills.append(backend_languages)
        needed_skills.append(frontend_languages)

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
        del team["meta"]
        team["team_id"] = team.pop("_id")
    return {"matches": matches}, 200

