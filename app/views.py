from flask import request
from app import app
from app.user_profile import get_user_profile, create_user_profile
from app.start_a_team import create_team
from app.add_team_member import add_member
from app.leave_team import leave
from app.team_recommendations import get_team_recommendations
from app.confirm_member import confirm
from app.individual_recommendations import get_individual_recommendations
from app.team_complete import mark_team_complete
from app.open_teams import get_open_teams
from app.team_profile import get_team_profile
from app.interested import user_interested

from app.util import format_string, return_resp
from app.schemas import ensure_json, ensure_user_logged_in, ensure_feature_is_enabled


@app.route("/user-profile", methods=["GET", "POST"])
@ensure_json()
@ensure_user_logged_in()
@ensure_feature_is_enabled("user profile")
def user_profile():
    data = request.get_json(silent=True)
    email = data["user_email"]
    email = email.strip().lower()
    if request.method == "GET":
        return get_user_profile(email)
    elif request.method == "POST":
        prizes = []
        skills = []
        if "prizes" in data:
            prizes = format_string(data["prizes"].strip().lower())
        if "skills" in data:
            skills = format_string(data["skills"].strip().lower())
        return create_user_profile(email, prizes=prizes, skills=skills)


@app.route("/start-a-team", methods=["POST"])
def start_a_team():
    return create_team()


@app.route("/leave-team", methods=["POST"])
@ensure_json()
@ensure_user_logged_in()
@ensure_feature_is_enabled("leave team")
def leave_team():
    data = request.get_json(silent=True)
    email = data["user_email"]
    email = email.strip().lower()
    return leave(email)


@app.route("/add-team-member", methods=["POST"])
def add_team_member():
    return add_member()


@app.route("/team-complete", methods=["POST"])
def team_complete():
    return mark_team_complete()


@app.route("/open-teams", methods=["GET"])
def open_teams():
    return get_open_teams()


@app.route("/team-profile", methods=["GET"])
def team_profile():
    return get_team_profile()


@app.route("/team-recommendations", methods=["GET"])
@ensure_json()
@ensure_user_logged_in()
@ensure_feature_is_enabled("team recommendations")
def team_recommendations():
    data = request.get_json(silent=True)
    email = data["user_email"]
    email = email.strip().lower()
    return get_team_recommendations(email)


@app.route("/individual-recommendations", methods=["GET"])
@ensure_json()
@ensure_user_logged_in()
@ensure_feature_is_enabled("individual recommendations")
def individual_recommendations():
    data = request.get_json(silent=True)
    email = data["user_email"]
    email = email.strip().lower()
    return get_individual_recommendations(email)


@app.route("/interested", methods=["POST"])
@ensure_json()
@ensure_user_logged_in()
@ensure_feature_is_enabled("interested")
def interested():
    data = request.get_json(silent=True)
    email = data["user_email"]
    email = email.strip().lower()
    if not data or "name" not in data or not data["name"]:
        return return_resp(401, "Missing inf")
    name = data["name"]
    return user_interested(email, name)


@app.route("/confirm-member", methods=["POST"])
def confirm_member():
    return confirm()
