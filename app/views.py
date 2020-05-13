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
def user_profile():
    return update_profile()


@app.route('/start-a-team', methods=['POST'])
def start_a_team():
    return create_team()


@app.route('/leave-team', methods=['POST'])
def leave_team():
    return leave()


@app.route('/add-team-member', methods=['POST'])
def add_team_member():
    return add_member()


@app.route('/team-complete', methods=['POST'])
def team_complete():
    return mark_team_complete()


@app.route('/open-teams', methods=['GET'])
def open_teams():
    return get_open_teams()


@app.route('/team-profile', methods=['GET'])
def team_profile():
    return get_team_profile()


@app.route('/team-recommendations', methods=['GET'])
def team_recommendations():
    return get_team_recommendations()


@app.route('/individual-recommendations', methods=['GET'])
def individual_recommendations():
    return get_individual_recommendations()


@app.route('/interested', methods=['POST'])
def interested():
    return user_interested()


@app.route('/confirm-member', methods=['POST'])
def confirm_member():
    return confirm()

