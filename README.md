# Team Builder

## Description

The purpose of this project is to help hackers find teammates who are interested in the same kinda project as they are. 

### API docs:
Read more on how to use the API [here](https://github.com/HackRU/teamRU/wiki/TeamRU-API).


### Flow:
User has to be logged in through lcs to be able to access their teambuilder profile <br/>
Completely new user: create hackrun account -> create teambuilder profile -> teambuilder dashboard <br/>
User with hackru account: create teambuilder profile -> teambuilder dashboard <br/>
User with hackru account and teambuilder profile -> teambuilder dashboard<br/>
Initially, we will only enable the create-profile feature for everyone to create their teambuilder profile so we can get everyone's info in the database before giving participants recommendations. After 2-3 weeks, we will enable all other features for people to find teammates and get recommendations.
 

### How to run the project:
1) clone the repo 
2) After cloning the repo, you have to add all the required info to the config file. You can find it in the teamBuilder chat.
3) cd to teamRU
4) run "pip3 install --user -r requirements.txt"
5) run "export FLASK_APP=run.py"
6) run "flask run"

### Next Steps:
1) Unit tests - not sure if i should have a separate db for this
2) Integrate lcs slack endpoint
3) Deploy
4) Improve the recommendations algorithm
5) Signin authentication flow - discuss with Shivan, Mickey and frontend team
    *I have my own login system for now to test but it shouldn't be used when we deploy
6) Set up a virtual env
