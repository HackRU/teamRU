from src.flaskapp.db import coll
from src.flaskapp.util import format_team_object
from fuzzywuzzy import fuzz


def parse_user_to_string(user):
    if not user:
        return {"message": "Invalid user or user not exist"}, 403

    interests = user["interests"]
    prizes = user["prizes"]
    bio = user["bio"]

    list_of_fields = interests
    list_of_fields.extend(prizes)
    list_of_fields.sort()
    bio += ''.join(list_of_fields)

    return bio


def lv_distance(user, user2):
    user_str = parse_user_to_string(user)
    team_mate_str = parse_user_to_string(user2)
    return fuzz.token_set_ratio(user_str, team_mate_str)


def get_team_recommendations(email):  # GET
    """Finds recommendations of teams for this individual to join

    The current matching algorithms finds teams that are not full already by matching on prizes and skills.

    Args:
        email: the email of the individual that wants recommendations of teams to join

    Return:
        a list of recommended teams to join
    """
    skills_weight = 1.2
    seriousness_weight = 1.1

    user = coll("users").find_one({"_id": email})
    if not user:
        return {"message": "Invalid user"}, 403

    # basic info about users
    skills = user["skills"]
    seriousness = user["seriousness"]

    all_open_teams = coll("teams").aggregate([{"$match": {"complete": False}}])
    all_open_members = coll("users").aggregate([{"$match": {"team_id": {"$all": [all_open_teams]}}}])

    team_map = dict()

    # map of distances
    for member in all_open_members:
        team_id = member["team_id"]
        dis = lv_distance(user, member)
        if team_id in team_map:
            team_map[team_id] = [dis]
        else:
            team_map[team_id].append(dis)

    # average the distance
    for list_key in team_map:
        member_list = team_map[list_key]
        team_map[list_key] = sum(member_list) / float(len(member_list))

    # match for skill
    needed_skills = set()
    frontend_languages = set(["html", "css", "javascript", "php", "typscript"])
    backend_languages = set(["java", "php", "ruby", "python", "c", "c++", "sql", "node.js"])

    # judging if the user if frontend or backend, and give backend suggestions if only know frontend, vice versa
    skill_set = set(skills)
    front_num = len(skill_set.intersection(frontend_languages))
    back_num = len(skill_set.intersection(backend_languages))

    front_pers = front_num/(front_num+back_num)
    back_pers = 1-front_pers
    if front_pers > back_pers:
        if front_pers < 0.3:
            needed_skills.update(frontend_languages)
        else:
            needed_skills.update(skill_set)
    else:
        if front_pers > 0.3:
            needed_skills.update(backend_languages)
        else:
            needed_skills.update(skill_set)

    for team_id in team_map:
        target_team = coll("teams").find_one({"_id": team_id})
        target_team_skills = target_team["skills"]
        intersection_size = len(set(target_team_skills).intersection(needed_skills))
        team_map[team_id] *= (intersection_size * skills_weight)
        team_seriousness = target_team["meta"]["seriousness"]
        team_map[team_id] = team_map[team_id] * (intersection_size * skills_weight) * \
                            (abs(seriousness-team_seriousness) * seriousness_weight)
    sorted_team_list = sorted(team_map.items(), key=lambda kv: (kv[1], kv[0]))

    bad_match_ids = set()
    bad_match_ids.add(user["team_id"])
    current_team = coll("teams").find_one({"_id": user["team_id"]})
    bad_match_ids.update(current_team["incoming_inv"])
    bad_match_ids.update(current_team["outgoing_inv"])
    good_matches = []

    for team_id in sorted_team_list[:, 0]:
        if team_id not in bad_match_ids:
            good_matches.append(team_id)

    if not good_matches:
        return {"message": "No recommendations found"}, 404

    for team in good_matches:
        del team["meta"]

    return {"matches": [format_team_object(team) for team in good_matches]}, 200
