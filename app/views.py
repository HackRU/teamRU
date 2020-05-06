from app import app
from app.user_profile import update_profile
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


@app.route('/user-profile', methods=['GET', 'POST'])
def user_profile(email, token):
    return update_profile(email, token)


@app.route('/start-a-team', methods=['POST'])
def start_a_team(email, token):
    return create_team(email, token)


@app.route('/leave-team', methods=['POST'])
def leave_team(email, token):
    return leave(email, token)


@app.route('/add-team-member', methods=['POST'])
def add_team_member(email, token):
    return add_member(email, token)


@app.route('/team-complete', methods=['POST'])
def team_complete(email, token):
    return mark_team_complete(email, token)


@app.route('/open-teams', methods=['GET'])
def open_teams(email, token):
    return get_open_teams(email, token)


@app.route('/team-profile', methods=['GET'])
def team_profile(email, token):
    return get_team_profile(email, token)


@app.route('/team-recommendations', methods=['GET'])
def team_recommendations(email, token):
    return get_team_recommendations(email, token)


@app.route('/individual-recommendations', methods=['GET'])
def individual_recommendations(email, token):
    return get_individual_recommendations(email, token)


@app.route('/interested', methods=['POST'])
def interested(email, token):
    return user_interested(email, token)


@app.route('/confirm-member', methods=['POST'])
def confirm_member(email, token):
    return confirm(email, token)

