from src.flaskapp.db import coll
from src.flaskapp.util import aggregate_team_meta


def get_team_profile(email, team_id):  # GET
    """Get team profile

    Fetches from the teams collection by using the team name as key.

    Args:
        User's email (str)
        Team name (str)

    Returns:
        User profile object (dict)
    """
    team = coll("teams").find_one({"_id": team_id})
    if not team:
        return {"message": "Team does not exist"}, 400

    if email not in team["members"]:
        return {"message": f'User not in team "{team_id}"'}, 403

    del team["meta"]

    return team, 200


def get_team_profiles(search):
    """Find teams that are open for new members

    Give a list of teams that fulfills the requirement and also still open for new members,
    if search is empty, returns all open team.

    Args:
        search: json file filter for complete, desc, skills and prizes

    Return:
        list of open teams that pass the filter.
    """
    if search is None:
        available_teams = coll("teams").find({"complete": False})
        all_open_teams = []
        for team in available_teams:
            del team["meta"]
            all_open_teams.append(team)
        if not all_open_teams:
            return {"message": "No open teams"}, 400
        return {"all_open_teams": all_open_teams}, 200

    search = search.strip.lower()
    available_teams = coll("teams").find(
        {
            "complete": False,
            "$or": [
                {"desc": {"$regex": ".*" + search + ".*"}},
                {"skills": {"$regex": ".*" + search + ".*"}},
                {"prizes": {"$regex": ".*" + search + ".*"}},
            ],
        }
    )
    all_open_teams = []
    for team in available_teams:
        del team["meta"]
        all_open_teams.append(team)
    if not all_open_teams:
        return {"message": "No open teams"}, 400
    return {"all_open_teams": all_open_teams}, 200


def create_team_profile(team_name, email, team_desc, skills, prizes):
    """Initialize team

    User creating a team

    Args:
        team_name: name of the team
        email: the email of the individual (already in a team) that wants other people to join his team recommendation
        team_desc: team description
        skills: Preferred skills for the team
        prizes: team goal/prize

    Return:
        response object(403:Invalid user, 401:Invalid name, 402:User In a team, 200: Success)
    """
    team_exist = coll("teams").find_one({"_id": team_name})
    user = coll("users").find_one({"_id": email})

    if not user:
        return {"message": "User does not exist"}, 404
    if team_exist:
        return {"message": "Team name already exists"}, 400

    if user["hasateam"]:
        return {"message": "User in a team"}, 400

    coll("users").update_one({"_id": email}, {"$set": {"hasateam": True}})
    coll("teams").insert(
        {
            "_id": team_name,
            "members": [email],
            "desc": team_desc,
            "skills": skills,
            "prizes": prizes,
            "complete": False,
            "incoming_inv": [],
            "outgoing_inv": [],
            "meta": aggregate_team_meta([email])
            # {
            # "skills": user["skills"],
            # "prizes": user["prizes"],
            # "interests": user["interests"],
            # },  # these are the fields that are aggregated internally
        }
    )
    return {"message": "Team profile successfully created"}, 201


# Should user have ability to change team name?
def update_team_profile(email, team_id, **kwargs):  # PUT
    """update team information

    returns team information as text in json, accept kwargs: desc, skills, prizes, interested

    Args:
        email: email of a team member

    Return:
        response object(401:User not in a team, 200: Success)
    """
    team = coll("teams").find_one({"_id": team_id})
    if not team:
        return {"message": "Team does not exist"}, 404

    if email not in team["members"]:
        return {"message": f'User not in team "{team_id}"'}, 403

    coll("teams").update_one({"_id": team_id}, {"$set": kwargs})

    return {"message": "Team profile successfully updated"}, 200
