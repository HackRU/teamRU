from flask import Flask, jsonify, request
import requests
import database


def validate(email: str, token: str):
    data = {"email": email, "token": token}
    resp = requests.post(base_url + "/validate", json=data)
    resp_parsed = resp.json()
    return resp_parsed


@app.route('/register', methods=['POST'])
def register(email: str, token: str):
    resp_parsed = validate(email, token)
    if resp_parsed["statusCode"] == 200:
        if (database.save_inf(email, request.form['skills'])) == 0:
            return jsonify({"statusCode": 400, "body": "You already have a profile"})
        if (database.save_skills(email, [request.form['slack'], request.form['github_handle'], request.form['no_of_hackathons']])) ==0:
            return jsonify({"statusCode": 400, "body": "These skills are listed in your portfolio"})
        return jsonify({"statusCode": 200, "body": "Information stored successfully"})
    else:
        return jsonify({"statusCode": 400, "body": resp_parsed["body"]})


@app.route('/match', methods=['POST'])
def match(email: str, token: str):
    resp_parsed = validate(email, token)
    if resp_parsed["statusCode"] == 200:
        candidates_emails = list(database.get_possible_candidates())
        profiles = database.get_profiles(candidates_emails)
        if profiles == None:
            return jsonify({"statusCode": 200, "profiles": "No participants with any of these skills are available"})
        return jsonify({"statusCode": 200, "body": profiles})
    else:
        return jsonify({"statusCode": 400, "body": resp_parsed["body"]})


@app.route('/team', methods=['POST'])
def team(email: str, token: str):
    resp_parsed = validate(email, token)
    if resp_parsed["statusCode"] == 200:
        database.has_team(email)
        return jsonify({"statusCode": 200, "body": "Congratulations On Completing Your Team"})
    else:
        return jsonify({"statusCode": 400, "body": resp_parsed["body"]})
