
LCS_BASE_URL = ""

DIRECTOR_CREDENTIALS = {
    "email":  "",
    "password": ""
}


# uri should contain auth and default database(database name)
DB_URI = "mongodb://127.0.0.1:27017/hackrd"


DB_COLLECTIONS = {
    "users": "users",
    "teams": "teams"
}


# 1 means that feature is enabled and 0 means that it is disabled
ENABLE_FEATURE = {
    "add team member": 1,
    "confirm member": 1,
    "individual recommendations": 1,
    "interested": 1,
    "leave team": 1,
    "open teams": 1,
    "start a team": 1,
    "team complete": 1,
    "team profile": 1,
    "team recommendations": 1,
    "user profile": 1
}
