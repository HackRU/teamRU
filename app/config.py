
LCS_BASE_URL = "https://api.hackru.org/dev"
 # *teamBuilder1
# https://hackru-team-builder.herokuapp.com/
DIRECTOR_CREDENTIALS = {
    "email":  "teambuilder@hackru.org",
    "password": "teambuilder"
}


# uri should contain auth and default database(database name)
DB_URI = "mongodb+srv://m001-student:amany@cluster0-vdddk.mongodb.net/hackru?retryWrites=true&w=majority"


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
