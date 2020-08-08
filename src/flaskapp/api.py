from flask import Flask, request

from src.flaskapp.db import coll
from src.users.user_profile import get_user_profile, create_user_profile
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

from src.flaskapp.util import format_string, return_resp
from src.flaskapp.schemas import (
    ensure_json,
    ensure_user_logged_in,
    ensure_feature_is_enabled,
)

app = Flask(__name__)


@app.route("/user-profile", methods=["GET", "POST"])
@ensure_json()
# @ensure_user_logged_in()
@ensure_feature_is_enabled("user profile")
def user_profile():
    data = request.get_json(silent=True)
    email = data["user_email"]
    email = format_string(email)
    if request.method == "GET":
        return get_user_profile(email)
    elif request.method == "POST":
        prizes = []
        skills = []
        if "prizes" in data:
            prizes = format_string(format_string(data["prizes"]))
        if "skills" in data:
            skills = format_string(format_string(data["skills"]))
        return create_user_profile(email, prizes=prizes, skills=skills)


@app.route("/start-a-team", methods=["POST"])
@ensure_json()
@ensure_user_logged_in()
@ensure_feature_is_enabled("start a team")
def start_a_team():
    data = request.get_json(silent=True)
    email = data["user_email"].strip().lower()
    if (
        not data
        or "name" not in data
        or "desc" not in data
        or "skills" not in data
        or not data["name"]
        or not data["desc"]
        or not data["skills"]
    ):
        return {"statusCode": 400, "body": "Required info not found"}
    team_name = data["name"].strip().lower()
    team_desc = data["desc"].strip().lower()
    partner_skills = data["skills"]
    formatted_skills = format_string(partner_skills)
    formatted_prizes = []
    if "prizes" in data:
        prizes = data["prizes"]
        formatted_prizes = format_string(prizes)
    return create_team(team_name, email, team_desc, formatted_skills, formatted_prizes)


@app.route("/leave-team", methods=["POST"])
@ensure_json()
@ensure_user_logged_in()
@ensure_feature_is_enabled("leave team")
def leave_team():
    data = request.get_json(silent=True)
    email = data["user_email"]
    email = format_string(email)
    return leave(email)


@ensure_json()
@ensure_user_logged_in()
@ensure_feature_is_enabled("add team member")
@app.route("/add-team-member", methods=["POST"])
def add_team_member():
    data = request.get_json(silent=True)
    email = data["user_email"].strip().lower()
    if not data or "email" not in data or not data["email"]:
        return return_resp(400, "Required info not found")
    partner_email = data["email"].strip().lower()
    return add_member(email, partner_email)


@ensure_json()
@ensure_user_logged_in()
@ensure_feature_is_enabled("team complete")
@app.route("/team-complete", methods=["POST"])
def team_complete():
    data = request.get_json(silent=True)
    email = data["user_email"]
    email = email.strip().lower()
    team = coll("teams").find_one({"members": {"$all": [email]}})
    if not team:
        return return_resp(401, "User not in a team")
    return mark_team_complete(team)


@ensure_json()
@ensure_user_logged_in()
@ensure_feature_is_enabled("open teams")
@app.route("/open-teams", methods=["GET"])
def open_teams():
    data = request.get_json(silent=True)
    if "filter" not in data or not data["filter"]:
        search = None
    else:
        search = data["filter"]

    return return_open_teams(search)


@ensure_json()
@ensure_user_logged_in()
@ensure_feature_is_enabled("team profile")
@app.route("/team-profile", methods=["GET"])
def team_profile():
    data = request.get_json(silent=True)
    email = data["user_email"]
    email = email.strip().lower()
    team = coll("teams").find_one({"members": {"$all": [email]}})
    if not team:
        return return_resp(400, "Team Not found")
    else:
        return get_team_profile(team)


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


@app.route("/interested", methods=["POST"])
@ensure_json()
@ensure_user_logged_in()
@ensure_feature_is_enabled("interested")
def interested():
    data = request.get_json(silent=True)
    email = data["user_email"]
    email = format_string(email)
    if not data or "name" not in data or not data["name"]:
        return return_resp(401, "Missing inf")
    name = data["name"]
    return user_interested(email, name)


@ensure_json()
@ensure_user_logged_in()
@ensure_feature_is_enabled("confirm member")
@app.route("/confirm-member", methods=["POST"])
def confirm_member():
    data = request.get_json(silent=True)
    email = data["user_email"].strip().lower()
    if not data or "email" not in data or not data["email"]:
        return return_resp(401, "Missing inf")
    hacker = data["email"].strip().lower()
    return confirm(email, hacker)
