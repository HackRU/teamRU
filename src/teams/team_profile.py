from src.flaskapp.lcs import call_auth_endpoint, get_name
from src.flaskapp.db import coll
from src.flaskapp.schemas import (
    ensure_json,
    ensure_user_logged_in,
    ensure_feature_is_enabled,
)


def get_team_profile(email, team_id):  # GET
    """get team information

       returns team information as text in json

       Args:
           email: email of a team member

       Return:
            Jsonified team info
       """
    email = email.strip().lower()
    team = coll("teams").find_one({"members": {"$all": [email]}})
    if not team:
        return {"message": "User not in a team"}, 401

    team_name = team["_id"]
    if team_name != team_id:
        return {"message": f"User not team {team_id}"}, 403

    members = team["members"]
    members_names = []
    for member in members:
        token = call_auth_endpoint()
        if token == 200:
            continue
        name = get_name(token, member)
        if name == 200:
            continue
        members_names.append(name)
        team.update({"names": members_names})
    return {"team": team}, 200


# TODO should user have ability to change team name?
def update_team_profile(email, team_id, **kwargs):  # PUT
    """update team information

          returns team information as text in json, accept kwargs: desc, skills, prizes, interested

          Args:
              email: email of a team member

          Return:
               response object(401:User not in a team, 200: Success)
          """
    email = email.strip().lower()
    team = coll("teams").find_one({"members": {"$all": [email]}})
    if not team:
        return {"message": "User not in a team"}, 401

    team_name = team["_id"]
    if team_name != team_id:
        return {"message": f"User not team {team_id}"}, 403

    desc = team["desc"]
    skills = team["skills"]
    prizes = team["prizes"]
    interests = team["interests"]

    # team_name = kwargs["id_"]
    if "desc" in kwargs.keys():
        desc = kwargs["desc"]
    if "skills" in kwargs.keys():
        skills = kwargs["skills"]
    if "prizes" in kwargs.keys():
        prizes = kwargs["prizes"]
    if "interests" in kwargs.keys():
        interests = kwargs["interests"]

    coll("teams").update(
        {"_id": team_name},
        {
            "$set": {
                "desc": desc,
                "skills": skills,
                "prizes": prizes,
                "interests": interests,
            }
        },
    )

    return {"message": "Team profile successfully updated"}, 200
