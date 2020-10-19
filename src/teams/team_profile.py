import shortuuid
from src.flaskapp.db import coll
from src.flaskapp.util import aggregate_team_meta


def get_team_profile(email, team_id):  # GET
    """Get team profile

    Fetches from the teams collection by using the team name as key.

    Args:
        User's email (str)
        Team name (str)

    Returns:
        Team profile object (dict)
    """
    team = coll("teams").find_one({"_id": team_id}, {"meta": False})
    if not team:
        return {"message": "Team does not exist"}, 400

    if email not in team["members"]:
        return {"message": f'User not in team "{team_id}"'}, 403

    team["team_id"] = team.pop("_id")
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
    all_open_teams = []
    if search is None:
        available_teams = coll("teams").find({"complete": False}, {"meta": False})
    else:
        search = search.strip().lower()
        available_teams = coll("teams").find(
            {
                "complete": False,
                "$or": [
                    {"desc": {"$regex": ".*" + search + ".*"}},
                    {"skills": {"$regex": ".*" + search + ".*"}},
                    {"prizes": {"$regex": ".*" + search + ".*"}},
                ],
            },
            {"meta": False},
        )

    for team in available_teams:
        team["team_id"] = team.pop("_id")
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

    user = coll("users").find_one({"_id": email})

    if not user:
        return {"message": "User does not exist"}, 404

    if user["hasateam"]:
        return {"message": "User in a team"}, 400

    random_id = shortuuid.ShortUUID().random(length=15)
    coll("users").update_one(
        {"_id": email}, {"$set": {"hasateam": True, "team_id": random_id}}
    )

    # Don't think we need a check but just incase if uuid is not strong enough
    # while True:  # make sure our id is not a repeat
    #     random_id = random.randint(1000, 9999)
    #     if not coll("teams").find_one({"_id": random_id}):
    #         break

    coll("teams").insert(
        {
            "_id": random_id,
            "name": team_name,
            "members": [email],
            "desc": team_desc,
            "skills": skills,
            "prizes": prizes,
            "complete": False,
            "incoming_inv": [],
            "outgoing_inv": [],
            "meta": aggregate_team_meta([email]),
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
