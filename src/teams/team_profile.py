import shortuuid
from src.flaskapp.db import coll
from src.flaskapp.util import aggregate_team_meta
import shortuuid


def get_team_profile(email, team_id):  # GET
    """Get team profile

    Fetches from the teams collection by using the team name as key.

    Args:
        User's email (str)
        Team name (str)

    Returns:
        User profile object (dict)
    """
    team = coll("teams").find_one({"_id": team_id}, {"meta": False})
    if not team:
        return {"message": "Team does not exist"}, 400

    if email not in team["members"]:
        return {"message": f'User not in team "{team_id}"'}, 403

    # del team["meta"]

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
        available_teams = coll("teams").find({"complete": False}, {"meta": False})
        all_open_teams = []
        for team in available_teams:
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
        },
        {"meta": False},
    )
    all_open_teams = []
    for team in available_teams:
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
    # team_exist = coll("teams").find_one({"_id": team_name}) #team name no longer need to be unique because we have uuid for "_id"

    user = coll("users").find_one({"_id": email})

    if not user:
        return {"message": "User does not exist"}, 404

    # if team_exist:
    #     return {"message": "Team name already exists"}, 400 #team name no longer need to be unique because we have uuid for "_id"

    if user["hasateam"]:
        return {"message": "User in a team"}, 400

<<<<<<< HEAD
    random_id = shortuuid.ShortUUID().random(length=15)
    coll("users").update_one(
        {"_id": email}, {"$set": {"hasateam": True, "team_id": random_id}}
    )
=======
    coll("users").update_one({"_id": email}, {"$set": {"hasateam": True}})
>>>>>>> badaa9e146651c8b5512779eecacb5471af97df7

    # Don't think we need a check but just incase if uuid is not strong enough
    # while True:  # make sure our id is not a repeat
    #     random_id = random.randint(1000, 9999)
    #     if not coll("teams").find_one({"_id": random_id}):
    #         break

    coll("teams").insert(
        {
<<<<<<< HEAD
            "_id": random_id,
=======
            "_id": shortuuid.ShortUUID().random(length=15),
>>>>>>> badaa9e146651c8b5512779eecacb5471af97df7
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
