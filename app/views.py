from flask import render_template, request
import requests
from app import app
from app.db import users, teams

base_url = ""


def call_validate_endpoint(email, token):
    data_dic = {"email": email, "token": token}
    resp = requests.post(base_url + "/validate", json=data_dic)
    resp_parsed = resp.json()
    if resp_parsed["statusCode"] == 400:
        '''{"statusCode":400,"body":"User email not found."}'''
        return resp_parsed
    if resp_parsed["statusCode"] == 403:
        '''{"statusCode": 403, "body": "Permission denied"}'''
        return resp_parsed
    if resp_parsed["statusCode"] == 200:
        return 200


def get_name(email, token):
    data_dic = {"email": email, "token": token, "query": {"email": email}}
    resp = requests.post(base_url + "/read", json=data_dic)
    resp_parsed = resp.json()
    return resp_parsed["body"]['first_name'] + "" + resp_parsed["body"]['last_name'] + ""


def format_string(s):
    if not s:
        return []
    elements = s.split(",")
    for ele in elements:
        ele.strip()
    return elements


@app.route('/start-a-team', methods=['POST'])
def start_a_team(email, token):
    if call_validate_endpoint(email, token) == 200:
        if request.method == 'POST':
            team_name = request.form['name'].strip().lower()
            if not team_name:
                return render_template('', result='Please provide a name for your team')
            team_exist = teams.find_one({"_id": team_name})
            if team_exist:
                return render_template('', result='Another team is using this name. Please choose another name')
            else:
                user_exist = users.find_one({"_id": email})
                if user_exist:
                    user_in_a_team = users.find_one({"_id": email, "hasateam": True})
                    if user_in_a_team:
                        return render_template('', result='You are already in a team')
                    else:
                        users.update_one({"_id": email}, {"$set": {"hasateam": True}})
                else:
                    users.insert({"_id": email, "hasateam": True})
                teams.insert({"_id": team_name, "members": [email]})
                return render_template('', result=team_name)
    else:
        return render_template('', result='Please try again')


@app.route('/leave-team', methods=['POST'])
def leave_team(email, token):
    if call_validate_endpoint(email, token) == 200:
        if request.method == 'POST':
            team_name = teams.find_one({"members": {"$all": [email]}}, {"_id"})['_id']
            team_size = len(teams.find_one({"_id": team_name})['members'])
            if team_size == 1:
                teams.delete_one({"_id": team_name})
            else:
                teams.update_one({"_id": team_name}, {"$pull": {"members": email}})
            users.update_one({"_id": email}, {"$set": {"hasateam": False}})
    else:
        return render_template('', result='Please try again')


@app.route('/add-team-member', methods=['POST'])
def add_team_member(email="amany.elgarf@gmail.com", token='42'):
    if call_validate_endpoint(email, token) == 200:
        if request.method == 'POST':
            partner_email = request.form['email'].strip().lower()
            # TO do -> use read endpoint to verify that a person is registered for hackru
            if not partner_email:
                return render_template('', result='Please provide an email for your partner')
            team_name = teams.find_one({"members": {"$all": [email]}}, {"_id"})['_id']
            team_size = len(teams.find_one({"_id": team_name})['members'])
            if team_size >= 4:
                return render_template('', result='A team can\'t have more than 4 members')
            user_exist = users.find_one({"_id": partner_email})
            if not user_exist:
                users.insert({"_id": partner_email, "hasateam": True})
                teams.update_one({"_id": team_name}, {"$push": {"members": partner_email}})
                return render_template('', result='You partner was successfully added to your team')
            else:
                partner_in_a_team = users.find_one({"_id": partner_email, "hasateam": True})
                if not partner_in_a_team:
                    users.update_one({"_id": partner_email}, {"$set": {"hasateam": True}})
                    teams.update_one({"_id": team_name}, {"$push": {"members": partner_email}})
                    return render_template('', result='You partner was successfully added to your team')
                else:
                    return render_template('', result='This person is already in a team')
    else:
        return render_template('', result='Please try again')


@app.route('/profile', methods=['GET', 'POST'])
def create_profile(email, token):
    #GET is used to get a profile while POST is used to create and update a profile
    if call_validate_endpoint(email, token) == 200:
        if request.method == 'GET':
            has_profile = users.find_one({"_id": email, "hasprofile": True})
            if not has_profile:
                return render_template('', result= "You don't have a team builder profile, please consider activating your profile first")
            profile = users.find_one({"_id": email})
            return render_template('', profile=profile)
        elif request.method == 'POST':
            tracks = request.form.getlist['track'].strip().lower()
            #Enter the skills separated by a comma. example: java, flask, backend
            skills = request.form['skills'].strip().lower()
            partner_skills = request.form['partner_skills'].strip().lower()
            slack_id = request.form['slack'].strip().lower()
            if not tracks or not skills or not partner_skills or not slack_id:
                return render_template('', result="Please fill out all the fields")
            formatted_skills = format_string(skills)
            formatted_partner_skills = format_string(partner_skills)
            user_exists = users.find({"_id": email})
            if user_exists:
                user_has_a_team = users.find({"_id": email, "hasateam": True})
                if user_has_a_team:
                    return render_template('', result= "You already have a team, you can only activate a team builder profile when you don't have team")
                has_profile = users.find_one({"_id": email, "hasprofile": True})
                if has_profile:
                    users.update({"_id": email}, {"skills": formatted_skills, "partner_skills": formatted_partner_skills, "slackid": slack_id, "tracks": tracks})
                    return render_template('', result= "Your profile has been updated")
                users.update({"_id": email}, {"hasprofile": True, "skills": formatted_skills, "partnerskills": formatted_partner_skills, "slackid": slack_id, "tracks": tracks})
                return render_template('', result="Your profile has been created")
            users.insert({"_id": email}, {"hasprofile": True, "skills": formatted_skills, "partnerskills": formatted_partner_skills, "slackid": slack_id, "tracks": tracks})
            return render_template('', result="Your profile has been created")
    else:
        return render_template('', result='Please try again')


@app.route('/get-recommendations', methods=['GET'])
def get_recommendations(email, token):
    if call_validate_endpoint(email, token) == 200:
        if request.method == 'GET':
            tracks = users.aggregate([
                {"$match": {"_id": email}}, {"$project": {"tracks": 1}}
            ])
            partner_skills = users.aggregate([
                {"$match": {"_id": email}}, {"$project": {"partner_skills": 1}}
            ])
            matches_emails = set()
            matches = []
            for track in tracks:
                match = users.aggregate([
                    {"hasateam": False, "tracks": {"$all": [track]}}, {"$project": {"email": 1, "skills": 1, "tracks": 1}}
                ])
                if not match:
                    continue
                else:
                    match_email = match['email']
                    if match_email not in matches_emails:
                        matches_emails.add(match_email)
                        matches.append(match)
            for skill in partner_skills:
                match = users.aggregate([
                    {"hasateam": False, "skills": {"$all": [skill]}}, {"$project": {"email": 1, "skills": 1, "tracks": 1}}
                ])
                if not match:
                    continue
                else:
                    match_email = match['email']
                    if match_email not in matches_emails:
                        matches_emails.add(match_email)
                        matches.append(match)
            if not matches:
                return render_template('', result='We couldn\'t find any members that match your criteria, try adding more skills')
            else:
                return render_template('', matches=matches)
    else:
        return render_template('', result='Please try again')


@app.route('/contact-person', methods=['POST'])
def contact_team(email, token):
    # Goal is to use the dm endpoint from lcs
    '''Not yet implemented'''
    if call_validate_endpoint(email, token) == 200:
        if request.method == 'POST':
            user_email = request.form['email']
            if not user_email:
                return render_template('', result='Please try again')
            slack_id = users.aggregate([{"match": {"_id": user_email}}, {"$project": {"slack_id": 1}}])
            if not slack_id:
                return render_template('', result='Please try again')
            return render_template('', slack_id=slack_id)
    else:
        return render_template('', result='Please try again')
