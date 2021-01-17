from src.flaskapp.db import coll
from src.flaskapp.util import format_team_object
from fuzzywuzzy import fuzz


def parse_user_to_string(user):
    if not user:
        return {"message": "Invalid user or user not exist"}, 403
    skills = user["skills"]
    interests = user["interests"]
    prizes = user["prizes"]
    bio = user["bio"]

    list_of_fields = skills
    list_of_fields.append(interests)
    list_of_fields.append(prizes)
    list_of_fields.sort()
    bio += ''.join(list_of_fields)

    return bio


def lv_distance(user, potential_teammates):
    user_str = parse_user_to_string(user)

    token_sort_ratio = []
    for each_user in potential_teammates:
        team_mate_str = parse_user_to_string(each_user)
        token_sort_ratio.append( fuzz.token_set_ratio(user_str, team_mate_str))
    return token_sort_ratio


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

    # basic info about users
    skills = user["skills"]
    interests = user["interests"]
    prizes = user["prizes"]
    seriousness = user["seriousness"]

    names = set()
    matches = []

    # match for skill
    needed_skills = set()
    frontend_languages = set(["html", "css", "javascript", "php", "typscript"])
    backend_languages = set(["java", "php", "ruby", "python", "c", "c++", "sql", "node.js"])
    # judging if the user if frontend or backend, and give backend suggestions if only know frontend, vice versa
    skill_set = set(skills)
    front_num = len(skill_set.intersection(skills))
    back_num = len(skill_set.intersection(skills))

    if front_num > (back_num * len(frontend_languages) / len(backend_languages)):
        if back_num < 3:
            needed_skills.update(backend_languages)
    else:
        if front_num < 3:
            needed_skills.update(frontend_languages)
    if len(needed_skills):
        needed_skills.update(backend_languages)
        needed_skills.update(frontend_languages)

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

    bad_match_ids = set()
    bad_match_ids.add(user["team_id"])
    current_team = coll("teams").find_one({"_id": user["team_id"]})
    bad_match_ids.update(current_team["incoming_inv"])
    bad_match_ids.update(current_team["outgoing_inv"])
    good_matches = []
    for team in matches:
        if team["_id"] not in bad_match_ids:
            good_matches.append(team)
    matches = good_matches

    if not matches:
        return {"message": "No recommendations found"}, 404

    for team in matches:
        del team["meta"]

    return {"matches": [format_team_object(team) for team in matches]}, 200
