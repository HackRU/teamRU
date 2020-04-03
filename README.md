# Team Builder

## Description

The purpose of this project is to help hackers find teammates who are interested in the same kinda project as they are. 

### API docs:
Read more on how to use the API [here](https://github.com/HackRU/teamRU/wiki/TeamRU-API).

### How to run the project:
1) clone the repo
* After cloning the repo, you have to add the db connnection string in db.py and the director account password in call_auth_endpoint() function in views .py. You can find them in the teamBuilder chat in discord.
2) cd to teamRU
3) run "pip3 install --user -r requirements.txt"
4) run "export FLASK_APP=run.py"
5) run "flask run"

### Next Steps:
1) Routing
2) Unit tests - not sure if i should have a separate db for this
3) Integrate lcs slack endpoint
4) Deploy
5) Improve the recommendations algorithm
6) Signin authentication flow - discuss with Shivan, Mickey and frontend team
    *I have my own login system for now to test but it shouldn't be used when we deploy
7) Set up a virtual env
