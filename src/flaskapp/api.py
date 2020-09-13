import base64
from flask import Flask, request

from src.flaskapp.db import coll
from src.users.user_profile import (
    get_user_profile,
    get_user_profiles,
    create_user_profile,
    update_user_profile,
)
from src.matching.individual_recommendations import get_individual_recommendations
from src.matching.team_recommendations import get_team_recommendations

from src.teams.team_profile import get_team_profile
from src.teams.open_teams import return_open_teams
from src.teams.team_complete import team_complete

# from src.teams.add_team_member import add_member

from src.teams.unify.team_invite import team_invite
from src.teams.unify.team_confirm import team_confirm
from src.teams.unify.team_rescind import team_rescind
from src.teams.unify.team_reject import team_reject

from src.users.user_leave import user_leave
from src.users.start_a_team import create_team


from src.flaskapp.util import format_string
from src.flaskapp.schemas import (
    ensure_json,
    ensure_user_logged_in,
    ensure_feature_is_enabled,
)

app = Flask(__name__)

############################## USERS ##############################


@app.route("/users", methods=["GET", "POST"])
# @ensure_json
# @ensure_user_logged_in
# @ensure_feature_is_enabled("user profile")
def users():
    if request.method == "GET":
        # Filter response using query parameters
        # Might need to add pagination (limit/offset) for this response
        return get_user_profiles(request.args)

    if request.method == "POST":
        # Create a new user
        data = request.get_json(silent=True)
        email = format_string(data["user_email"])

        prizes = []
        skills = []
        bio = ""
        github = ""

        if "prizes" in data:
            prizes = format_string(data["prizes"])
        if "skills" in data:
            skills = format_string(data["skills"])
        if "bio" in data:
            bio = format_string(data["bio"])
        if "github" in data:
            # NOTE can ping github api to verify this is an actual acct.
            github = format_string(data["github"])

        return create_user_profile(
            email, prizes=prizes, skills=skills, bio=bio, github=github
        )


@app.route("/users/<user_id>", methods=["GET", "PUT"])
# @ensure_json
# @ensure_user_logged_in
# @ensure_feature_is_enabled("user profile")
def single_user(user_id):
    # Decode base64 encoded string
    # urlsafe_b64decode takes in a binary string, which is why we need to encode/decode (convert to binary/string)
    # email = base64.urlsafe_b64decode(user_id.encode()).decode()
    email = user_id
    if request.method == "GET":
        # Retrieve a single user
        return get_user_profile(email)

    if request.method == "PUT":
        data = request.get_json(silent=True)

        temp = {
            name: format_string([data[name]])
            for name in ["prizes", "skills", "bio", "github"]
            if data.get(name)
        }
        return update_user_profile(email, **temp)


# # NOTE Removed
# @app.route("/users/<user_id>/invite", methods=["POST"])
# # @ensure_json
# # @ensure_user_logged_in
# # @ensure_feature_is_enabled("interested")
# def single_team_interested(user_id):
#     # TODO: A user makes a request to join a team
#     # TODO: Add team_id or some sort of team identifier
#     data = request.get_json(silent=True)
#     email = data["user_email"]
#     email = format_string(email)
#     if not data or "name" not in data or not data["name"]:
#         return {"message": "Missing inf"}, 401
#     name = data["name"]
#     return user_interested(email, name)

# # NOTE Removed
# @app.route("/users/<user_id>/confirm", methods=["POST"]) #Post
# # @ensure_json
# # @ensure_user_logged_in
# # @ensure_feature_is_enabled("interested")
# def confirm_invite(user_id):
#     # TODO This method has not been implemented yet and the name of the method name can be changed to better suit the action
#     # TODO: A user accpets a team's request to join their team
#     # TODO: Add team_id or some sort of team identifier
#     data = request.get_json(silent=True)
#     email = data["user_email"]
#     email = format_string(email)
#     if not data or "name" not in data or not data["name"]:
#         return {"message": "Missing inf"}, 401
#     name = data["name"]
#     return user_interested(email, name)


############################## TEAMS ##############################


@app.route("/teams", methods=["GET", "POST"])
# @ensure_json
# @ensure_user_logged_in
# @ensure_feature_is_enabled("start a team")
def teams():
    if request.method == "GET":
        # Previously /open-teams
        # TODO Convert this code to accept filters from query params
        data = request.get_json(silent=True)
        if "filter" not in data or not data["filter"]:
            search = None
        else:
            search = data["filter"]
        return return_open_teams(search)

    if request.method == "POST":
        # Previously /start-a-team
        data = request.get_json(silent=True)
        email = format_string(data["user_email"])

        if (
            not data
            or "name" not in data
            or "desc" not in data
            or "skills" not in data
            or not data["name"]
            or not data["desc"]
            or not data["skills"]
        ):
            return {"message": "Required info not found"}, 400
        team_name = format_string(data["name"])
        team_desc = format_string(data["desc"])
        skills = format_string(data["skills"])
        prizes = []
        if "prizes" in data:
            prizes = format_string(data["prizes"])
        return create_team(team_name, email, team_desc, skills, prizes)


@app.route("/teams/<user_id>", methods=["GET", "PUT"])
# @ensure_json
# @ensure_user_logged_in
# @ensure_feature_is_enabled("start a team")
def single_team(user_id):
    email = base64.urlsafe_b64decode(user_id.encode()).decode()

    if request.method == "GET":
        return get_team_profile(email)

    if request.method == "PUT":
        # TODO: Daniel - Update team profile (similar to update user profile)
        pass


@app.route("/teams/<user_id>/complete", methods=["PUT"])
# @ensure_json
# @ensure_user_logged_in
# @ensure_feature_is_enabled("team complete")
def mark_team_complete(user_id):
    if request.method == "PUT":
        # Previously /team-complete
        data = request.get_json(silent=True)
        email = data["user_email"]
        email = email.strip().lower()
        team = coll("teams").find_one({"members": {"$all": [email]}})
        if not team:
            return {"message": "User not in a team"}, 401
        return team_complete(team)


# TODO Group admins? They can remove, transfer adminship, etc.
@app.route("/teams/<user_id>/leave", methods=["POST"])
# @ensure_json
# @ensure_user_logged_in
# @ensure_feature_is_enabled("leave team")
def leave(user_id):
    data = request.get_json(silent=True)
    email = data["user_email"]
    email = format_string(email)
    return user_leave(email)


############################## UNITY ##############################
@app.route("/teams/<team_id>/invite", methods=["POST"])
# @ensure_json
# @ensure_user_logged_in
# @ensure_feature_is_enabled("add team member")
def invite(team_id):
    # NOTE team1 -inviting-> team2 (invite another team)
    team1_name = team_id
    # team1_name = base64.urlsafe_b64decode(team_id.encode()).decode()
    data = request.get_json(silent=True)
    if not data or "name" not in data or not data["name"]:
        return {"message": "Required info not found"}, 400
    team2_name = format_string(data["name"])
    return team_invite(team1_name, team2_name)


@app.route("/teams/<team_id>/confirm", methods=["POST"])
# @ensure_json
# @ensure_user_logged_in
# @ensure_feature_is_enabled("confirm member")
def confirm(team_id):
    # NOTE team1 -confirms-> team2 (confirm an invite)
    team1_name = team_id
    # team1_name = base64.urlsafe_b64decode(team_id.encode()).decode()
    data = request.get_json(silent=True)
    if not data or "name" not in data or not data["name"]:
        return {"message": "Required info not found"}, 400
    team2_name = format_string(data["name"])
    return team_confirm(team1_name, team2_name)


@app.route("/teams/<team_id>/rescind", methods=["POST"])
def rescind(team_id):
    # NOTE team1 -rescind-> team2 (rescind an invite)
    team1_name = team_id
    # team1_name = base64.urlsafe_b64decode(team_id.enconde()).decode()
    data = request.get_json(silent=True)
    if not data or "name" not in data or not data["name"]:
        return {"message": "Required info not found"}, 400
    team2_name = format_string(data["name"])
    return team_rescind(team1_name, team2_name)


@app.route("/teams/<team_id>/reject", methods=["POST"])
def reject(team_id):
    # NOTE team1 -reject-> team2 (rejecting an invite)
    team1_name = team_id
    # team1_name = base64.urlsafe_b64decode(team_id.enconde()).decode()
    data = request.get_json(silent=True)
    if not data or "name" not in data or not data["name"]:
        return {"message": "Required info not found"}, 400
    team2_name = format_string(data["name"])
    return team_reject(team1_name, team2_name)


############################## MATCHES ##############################


@app.route("/team-recommendations", methods=["GET"])
# @ensure_json
# @ensure_user_logged_in
# @ensure_feature_is_enabled("team recommendations")
def team_recommendations():
    data = request.get_json(silent=True)
    email = data["user_email"]
    email = format_string(email)
    return get_team_recommendations(email)


@app.route("/individual-recommendations", methods=["GET"])
# @ensure_json
# @ensure_user_logged_in
# @ensure_feature_is_enabled("individual recommendations")
def individual_recommendations():
    data = request.get_json(silent=True)
    email = data["user_email"]
    email = format_string(email)
    return get_individual_recommendations(email)
