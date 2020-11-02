import shortuuid
from src.flaskapp.db import coll
from src.flaskapp.util import aggregate_team_meta, format_team_object


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

    return format_team_object(team), 200


def get_team_profiles(email, search, offset, limit):
    """Find teams that are open for new members

    Give a list of teams that fulfills the requirement and also still open for new members,
    if search is empty, returns all open teams (according to offset/limit).

    Note: Along with .skip() and .limit() for the offset and limit parameters, we also need
    to use .sort() because the order of records returned by a MongoDB cursor isn't guaranteed
    to be the same every time. We are sorting by ascending _id, which is random (shortUUID).

    Args:
        search: json file filter for complete, desc, skills and prizes
        offset: the number of teams to skip before selecting teams for the response (default 0)
        limit: the number of teams to return in the response (default 10)

    Return:
        list of open teams that pass the filter.
    """
    user = coll("users").find_one({"_id": email})
    team = coll("teams").find_one({"_id": user["team_id"]}, {"meta": False})
    do_not_show = set()
    do_not_show.add(team["_id"])
    do_not_show.update(team["outgoing_inv"])
    do_not_show.update(team["incoming_inv"])
    total_teams = coll("teams").find({"complete": False}).count() - len(do_not_show)

    all_open_teams = []
    if search is None:
        available_teams = (
            coll("teams")
            .find({"complete": False, "_id": {"$nin": list(do_not_show)}}, {"meta": False})
            .sort("_id", 1)
            .skip(offset)
            .limit(limit)
        )
    else:
        search = search.strip().lower()
        available_teams = (
            coll("teams")
            .find(
                {
                    "complete": False,
                    "_id": {"$nin": list(do_not_show)},
                    "$or": [
                        {"desc": {"$regex": ".*" + search + ".*"}},
                        {"skills": {"$regex": ".*" + search + ".*"}},
                        {"prizes": {"$regex": ".*" + search + ".*"}},
                    ],
                },
                {"meta": False},
            )
            .sort("_id", 1)
            .skip(offset)
            .limit(limit)
        )

    for team in available_teams:
        all_open_teams.append(format_team_object(team))

    if not all_open_teams:
        return {"message": "No open teams", "total_teams": total_teams}, 400
    return {"all_open_teams": all_open_teams, "total_teams": total_teams}, 200


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
        team_id: id of the team
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
