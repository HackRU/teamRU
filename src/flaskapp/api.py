from coolname import generate_slug

from flask import Flask, request
from flask_cors import CORS

from src.users.user_profile import (
    get_user_profile,
    get_user_profiles,
    create_user_profile,
    update_user_profile,
)

from src.teams.team_profile import (
    get_team_profile,
    get_team_profiles,
    create_team_profile,
    update_team_profile,
)
from src.teams.team_complete import team_complete
from src.teams.user_leave import user_leave

from src.teams.unify.team_invite import team_invite
from src.teams.unify.team_confirm import team_confirm
from src.teams.unify.team_rescind import team_rescind
from src.teams.unify.team_reject import team_reject
from src.teams.unify.user_invite import user_invite

from src.matching.team_recommendations import get_team_recommendations

from src.forum.forum_get import (
    get_all_posts,
    get_all_comments,
    get_all_subcomments,
    get_user_posts
)
from src.forum.forum_post import (
    post_post,
    post_comment,
    post_subcomment
)


from src.flaskapp.util import format_string
from src.flaskapp.auth import authenticate


app = Flask(__name__)
CORS(app)


@app.route("/", methods=["GET"])
def index():
    return {"message": "Welcome to TeamRU!"}, 200


############################## USERS ##############################


@app.route("/users", methods=["GET", "POST"])
@authenticate
def users(email):

    if request.method == "GET":
        # Filter response using query parameters
        # Might need to add pagination (limit/offset) for this response
        return get_user_profiles(request.args)

    if request.method == "POST":
        # Create a new user
        data = request.get_json(silent=True)
        prizes = []
        skills = []
        interests = []
        bio = ""
        github = ""
        seriousness = 3

        if "prizes" in data:
            prizes = format_string(data["prizes"])
        if "skills" in data:
            skills = format_string(data["skills"])
        if "interests" in data:
            interests = format_string(data["interests"])
        if "bio" in data:
            bio = format_string(data["bio"])
        if "github" in data:
            # NOTE can ping github api to verify this is an actual acct.
            github = format_string(data["github"])
        if "seriousness" in data:
            try:
                seriousness = int(data["seriousness"])
            except ValueError:
                pass
        return create_user_profile(
            email,
            prizes=prizes,
            skills=skills,
            bio=bio,
            github=github,
            interests=interests,
            seriousness=seriousness,
        )


@app.route("/users/profile", methods=["GET", "PUT"])
@authenticate
def single_user(email):
    if request.method == "GET":
        # Retrieve a single user
        return get_user_profile(email)

    if request.method == "PUT":
        data = request.get_json(silent=True)

        kwargs = {
            name: format_string(data[name])
            for name in [
                "prizes",
                "skills",
                "bio",
                "github",
                "interests",
                "seriousness",
            ]
            if data.get(name)
        }
        return update_user_profile(email, **kwargs)


############################## TEAMS ##############################


@app.route("/teams", methods=["GET", "POST"])
@authenticate
def teams(email):
    if request.method == "GET":
        search = request.args.get("filter", None)
        try:
            offset = int(request.args.get("offset"))
        except:
            offset = 0

        try:
            limit = int(request.args.get("limit"))
        except:
            limit = 10

        return get_team_profiles(email, search, offset, limit)

    if request.method == "POST":
        data = request.get_json(silent=True)

        if (
            not data
            or "name" not in data
            or "desc" not in data
            or not data["name"]
            or not data["desc"]
        ):
            return {"message": "Required info not found"}, 400
        team_name = format_string(data["name"])
        team_desc = format_string(data["desc"])
        skills = []
        if "skills" in data:
            skills = format_string(data["skills"])
        prizes = []
        if "prizes" in data:
            prizes = format_string(data["prizes"])
        return create_team_profile(team_name, email, team_desc, skills, prizes)


@app.route("/teams/<team_id>", methods=["GET", "PUT"])
@authenticate
def single_team(email, team_id):
    if request.method == "GET":
        return get_team_profile(email, team_id)

    if request.method == "PUT":
        data = request.get_json(silent=True)

        kwargs = {
            name: format_string(data[name])
            for name in ["name", "desc", "skills", "prizes"]
            if data.get(name)
        }
        return update_team_profile(email, team_id, **kwargs)


@app.route("/teams/<team_id>/complete", methods=["PUT"])
@authenticate
def mark_team_complete(email, team_id):
    return team_complete(email, team_id)


@app.route("/teams/<team_id>/leave", methods=["PUT"])
@authenticate
def leave(email, team_id):
    response = user_leave(email, team_id)
    create_team_profile(generate_slug(), email, "Edit Me :D", [], [])
    return response


############################## UNIFY ##############################


@app.route("/teams/<team1_id>/invite", methods=["POST"])
@authenticate
def invite(email, team1_id):
    # NOTE team1 -inviting-> team2 (invite another team)
    # team1_name = team_id
    data = request.get_json(silent=True)
    if not data or "team2_id" not in data or not data["team2_id"]:
        return {"message": "Required info not found"}, 400
    team2_id = data["team2_id"]
    return team_invite(email, team1_id, team2_id)


@app.route("/teams/<team1_id>/confirm", methods=["POST"])
@authenticate
def confirm(email, team1_id):
    # NOTE team1 -confirms-> team2 (confirm an invite)
    # team1_name = team_id
    data = request.get_json(silent=True)
    if not data or "team2_id" not in data or not data["team2_id"]:
        return {"message": "Required info not found"}, 400
    team2_id = data["team2_id"]
    return team_confirm(email, team1_id, team2_id)


@app.route("/teams/<team1_id>/rescind", methods=["POST"])
@authenticate
def rescind(email, team1_id):
    # NOTE team1 -rescind-> team2 (rescind an invite)
    # team1_name = team_id
    data = request.get_json(silent=True)
    if not data or "team2_id" not in data or not data["team2_id"]:
        return {"message": "Required info not found"}, 400
    team2_id = data["team2_id"]
    return team_rescind(email, team1_id, team2_id)


@app.route("/teams/<team1_id>/reject", methods=["POST"])
@authenticate
def reject(email, team1_id):
    # NOTE team1 -reject-> team2 (rejecting an invite)
    # team1_name = team_id
    data = request.get_json(silent=True)
    if not data or "team2_id" not in data or not data["team2_id"]:
        return {"message": "Required info not found"}, 400
    team2_id = data["team2_id"]
    return team_reject(email, team1_id, team2_id)


@app.route("/teams/<team1_id>/invite/user", methods=["POST"])
@authenticate
def invite_user(email, team1_id):
    # NOTE team1 -inviting-> user2 (invite another 1 person team)
    data = request.get_json(silent=True)
    if not data or "user_email" not in data or not data["user_email"]:
        return {"message": "Required info not found"}, 400
    user2_email = data["user_email"]
    return user_invite(email, team1_id, user2_email)


############################## MATCHES ##############################


@app.route("/matches/<team_id>", methods=["GET"])
@authenticate
def team_recommendations(email, team_id):
    # WIP
    return get_team_recommendations(email)
    email = None
    team_id = None
    return {"message": "placeholder"}, 200



############################## FORUM ##############################
@app.route("/forum/all_posts", methods=["GET"])
@authenticate
def all_posts(limit=100):
    return get_all_posts(limit)


@app.route("/forum/all_comments/<uuid>", methods=["GET"])
@authenticate
def all_comments(uuid):
    return get_all_comments(uuid)


@app.route("/forum/all_subcomments/<uuid>", methods=["GET"])
@authenticate
def all_subcomments(uuid):
    return get_all_subcomments(uuid)


@app.route("/forum/user_posts/<email>", methods=["GET"])
@authenticate
def user_posts(email, limit=100):
    return get_user_posts(email, limit)


############################## FORUM_post ##############################


@app.route("/forum/post", methods=["POST"])
@authenticate
def post():
    data = request.get_json(silent=True)
    kwargs = {
        "poster": data["poster"],
        "title": data["title"],
        "content": data["content"]
    }
    return post_post(kwargs)



@app.route("/forum/<uuid>/comment", methods=["POST"])
@authenticate
def comment(uuid, limit=100):
    data = request.get_json(silent=True)
    kwargs = {
        "parent_uuid": uuid,
        "poster": data["poster"],
        "content": data["content"]
    }
    return post_comment(kwargs)


@app.route("/forum/<uuid>/subcomment", methods=["POST"])
@authenticate
def subcomment(uuid, limit=100):
    data = request.get_json(silent=True)
    kwargs = {
        "parent_uuid": uuid,
        "poster": data["poster"],
        "content": data["content"]
    }
    return post_subcomment(kwargs)