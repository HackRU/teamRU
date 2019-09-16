import mysql.connector as ms
from flask import request


def open_database_connection():
    return ms.connect(user='admin', password='hypxpqVtPqljtCdai3eC',
                     host='teambuilder-dev.c2zevowxpqek.us-east-2.rds.amazonaws.com',
                     database='innodb')


def save_inf(email: str, inf: str):
    splited_list = inf.split(",")
    cnx = open_database_connection()
    mycursor = cnx.cursor()
    for i in splited_list:
        query = "INSERT INTO innodb.skills  (email, skill ) VALUES ('" + email + "', '" + i.strip().lower() + "')"
        try:
            mycursor.execute(query)
        except ms.IntegrityError as err:
            cnx.close()
            return 0
        cnx.commit()
    cnx.close()


def save_skills(email: str, inf: []):
    cnx = open_database_connection()
    mycursor = cnx.cursor()
    query = "INSERT INTO innodb.participants (email, slack, github_handle, no_of_hackathons) VALUES ('" + email + "', '" + inf[0].lower() + "', '" + inf[1].lower() + "', " + str(inf[2]) + ")"
    try:
        mycursor.execute(query)
    except ms.IntegrityError as err:
        cnx.close()
        return 0
    cnx.commit()
    cnx.close()


def get_possible_candidates():
    hackathons = request.form['no_of_hackathons']
    skills = request.form['skills']
    skills_list = skills.split(",")
    emails = set()
    cnx = open_database_connection()
    mycursor = cnx.cursor()
    for language in skills_list:
        query = "SELECT p.email from innodb.participants p ,innodb.skills l where p.email = l.email and p.no_of_hackathons >= '" + str(hackathons) + "'  and l.skill = '" + language.strip().lower() + "'"
        mycursor.execute(query)
        emails = emails.union(set(mycursor.fetchall()))
    cnx.close()
    return emails


def get_profiles(candidates_emails):
    cnx = open_database_connection()
    mycursor = cnx.cursor()
    profiles = []
    for candidate in candidates_emails:
        query_one = "SELECT * from innodb.participants p where p.email = '" + candidate[0] + "'"
        mycursor.execute(query_one)
        result = []
        for i in mycursor.fetchall()[0]:
            result.append(i)
        query_two = "SELECT s.skill from innodb.skills s where s.email = '" + candidate[0] + "'"
        mycursor.execute(query_two)
        skills = []
        for k in mycursor.fetchall():
            skills.append(k[0])
        result.append(skills)
        r = {"email": result[0], "slack": result[1], "github": result[2], "hackathons": result[3], "skills": result[4]}
        profiles.append(r)
    return profiles


def has_team(email):
    cnx = open_database_connection()
    mycursor = cnx.cursor()
    query = "INSERT INTO innodb.team (email) VALUES ('" + email + "')"
    mycursor.execute(query)
    cnx.commit()
    cnx.close()