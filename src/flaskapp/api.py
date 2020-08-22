import base64
from flask import Flask, request

from src.flaskapp.db import coll
from src.users.user_profile import get_user_profile, create_user_profile, update_user_profile
from src.users.individual_recommendations import get_individual_recommendations
from src.users.team_recommendations import get_team_recommendations
from src.users.interested import user_interested
from src.users.leave_team import leave

from src.teams.team_profile import get_team_profile
from src.teams.open_teams import return_open_teams
from src.teams.start_a_team import create_team
from src.teams.add_team_member import add_member
from src.teams.confirm_member import confirm
from src.teams.team_complete import mark_team_complete

from src.flaskapp.util import format_string
from src.flaskapp.schemas import (
    ensure_json,
    ensure_user_logged_in,
    ensure_feature_is_enabled,
)

app = Flask(__name__)

############################## USERS ##############################

@app.route("/users", methods=["GET", "POST"])
# @ensure_json()
# @ensure_user_logged_in()
# @ensure_feature_is_enabled("user profile")
def users():
    if request.method == "GET":
        # TODO Retrieve all users currently in TeamRU
        # Filter response using query parameters
        # Might need to add pagination (limit/offset) for this response
        return {}, 200 # placeholder

    if request.method == "POST":
        # Create a new user
        data = request.get_json(silent=True)
        email = format_string(data["user_email"])

        prizes = []
        skills = []
        if "prizes" in data:
            prizes = format_string(data["prizes"])
        if "skills" in data:
            skills = format_string(data["skills"])
        return create_user_profile(email, prizes=prizes, skills=skills)

@app.route("/users/<user_id>", methods=["GET", "PUT"])
# @ensure_json()
# @ensure_user_logged_in()
# @ensure_feature_is_enabled("user profile")
def single_user(user_id):
    # Decode base64 encoded string
    # urlsafe_b64decode takes in a binary string, which is why we need to encode/decode (convert to binary/string)
    email = base64.urlsafe_b64decode(user_id.encode()).decode()

    if request.method == "GET":
        # Retrieve a single user
        return get_user_profile(email)

    if request.method == "PUT":
        data = request.get_json(silent=True)

        # Create a new user
        prizes = []
        skills = []
        if "prizes" in data:
            prizes = format_string(data["prizes"])
        if "skills" in data:
            skills = format_string(data["skills"])
        return update_user_profile(email, prizes=prizes, skills=skills)

@app.route("/users/<user_id>/invite", methods=["POST"])
@ensure_json()
@ensure_user_logged_in()
@ensure_feature_is_enabled("interested")
def single_team_interested(user_id):
    # TODO: A user makes a request to join a team
    # TODO: Add team_id or some sort of team identifier
    data = request.get_json(silent=True)
    email = data["user_email"]
    email = format_string(email)
    if not data or "name" not in data or not data["name"]:
        return {"message": "Missing inf"},401 
    name = data["name"]
    return user_interested(email, name)

@app.route("/users/<user_id>/confirm", methods=["POST"])
@ensure_json()
@ensure_user_logged_in()
@ensure_feature_is_enabled("interested")
def single_team_interested(user_id):
    # TODO: A user accpets a team's request to join their team
    # TODO: Add team_id or some sort of team identifier
    data = request.get_json(silent=True)
    email = data["user_email"]
    email = format_string(email)
    if not data or "name" not in data or not data["name"]:
        return {"message":"Missing inf"}, 401
    name = data["name"]
    return user_interested(email, name)

############################## TEAMS ##############################

@app.route("/teams", methods=["GET", "POST"])
# @ensure_json()
# @ensure_user_logged_in()
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
            # TODO use return_resp (done)
            return {"message": "Required info not found"}, 400
        team_name = format_string(data["name"])
        team_desc = format_string(data["desc"])
        skills = format_string(data["skills"])
        prizes = []
        if "prizes" in data:
            prizes = format_string(data["prizes"])
        return create_team(team_name, email, team_desc, skills, prizes)

@app.route("/teams/<user_id>", methods=["GET", "PUT"])
# @ensure_json()
# @ensure_user_logged_in()
# @ensure_feature_is_enabled("start a team")
def single_team(user_id):
    if request.method == "GET":
        # Previously /team-profile
        # TODO Update this to use user_id   (done)
        # TODO Remove coll from this file - db processing should not be here(done)
        # data = request.get_json(silent=True) (uncertain usage)
        email = base64.urlsafe_b64decode(user_id.encode()).decode()
        return get_team_profile(email)

    if request.method == "PUT":
        # TODO Update team profile （what can the team update)
        

@app.route("/teams/<user_id>/complete", methods=["PUT"])
# @ensure_json()
# @ensure_user_logged_in()
# @ensure_feature_is_enabled("team complete")
def single_team_complete(user_id):
    if request.method == "PUT":
        # Previously /team-complete
        data = request.get_json(silent=True)
        email = data["user_email"]
        email = email.strip().lower()
        team = coll("teams").find_one({"members": {"$all": [email]}})
        if not team:
            return {"message": "User not in a team"}, 401
        return mark_team_complete(team)

# TODO Group admins? They can remove, transfer adminship, etc.
@app.route("/teams/<user_id>/leave", methods=["POST"])
# @ensure_json()
# @ensure_user_logged_in()
# @ensure_feature_is_enabled("leave team")
def single_team_leave(user_id):
    data = request.get_json(silent=True)
    email = data["user_email"]
    email = format_string(email)
    return leave(email)

@app.route("/teams/<user_id>/confirm", methods=["POST"])
# @ensure_json()
# @ensure_user_logged_in()
# @ensure_feature_is_enabled("confirm member")
def confirm_member():
    # TODO When someone on the team accepts a user's request to join the team
    data = request.get_json(silent=True)
    email = data["user_email"].strip().lower()
    if not data or "email" not in data or not data["email"]:
        return {"message": "Missing inf"}, 401
    hacker = data["email"].strip().lower()
    return confirm(email, hacker)

@app.route("/teams/<user_id>/invite", methods=["POST"])
@ensure_json()
@ensure_user_logged_in()
@ensure_feature_is_enabled("add team member")
def add_team_member():
    # TODO Someone on the team is inviting another user to the team
    data = request.get_json(silent=True)
    email = data["user_email"].strip().lower()
    if not data or "email" not in data or not data["email"]:
        return {"message":"Required info not found"}, 400
    partner_email = data["email"].strip().lower()
    return add_member(email, partner_email)

############################## MATCHES ##############################

@app.route("/team-recommendations", methods=["GET"])
@ensure_json()
@ensure_user_logged_in()
@ensure_feature_is_enabled("team recommendations")
def team_recommendations():
    data = request.get_json(silent=True)
    email = data["user_email"]
    email = format_string(email)
    return get_team_recommendations(email)


@app.route("/individual-recommendations", methods=["GET"])
@ensure_json()
@ensure_user_logged_in()
@ensure_feature_is_enabled("individual recommendations")
def individual_recommendations():
    data = request.get_json(silent=True)
    email = data["user_email"]
    email = format_string(email)
    return get_individual_recommendations(email)
