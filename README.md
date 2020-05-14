# Team Builder

## Description

The purpose of this project is to help hackers find teammates who are interested in the same kinda project as they are. 

### API docs:
Read more on how to use the API [here](https://github.com/HackRU/teamRU/wiki/TeamRU-API).


### Application Flow:
User has to be logged in through lcs to be able to access their teambuilder profile <br/>
Completely new user: create hackrun account -> create teambuilder profile -> teambuilder dashboard <br/>
User with hackru account: create teambuilder profile -> teambuilder dashboard <br/>
User with hackru account and teambuilder profile -> teambuilder dashboard<br/>
Initially, we will only enable the create-profile feature for everyone to create their teambuilder profile so we can get everyone's info in the database before giving participants recommendations. After 2-3 weeks, we will enable all other features for people to find teammates and get recommendations.
 
 
### Signin Authentication Flow:
Since teambuilder will be part of the main hackru website, I figured that the best way to integrate it with lcs is to pass the email and token each time there is a call to any of the endpoints. TeamBuilder doesn't have its own login system/sessions. Every time there is a call to any of the endpoints and the email and token are passed, validate endpoint from lcs is called to verify that the user is indeed logged in and his session is not expired. 


### Deployment:
- The API is now deployed at [https://hackru-team-builder.herokuapp.com/](https://hackru-team-builder.herokuapp.com/) for testing <br/>
- The Deployed version is connected to dev <br/>
- Will add information on how to manually test it through lcs soon until I write the automated tests


### Running the API locally:
1) clone the repo 
2) After cloning the repo, you have to add all the required info to the config file. You can find it in the teamBuilder chat.
3) cd to teamRU
4) run "pip3 install --user -r requirements.txt"
5) run "export FLASK_APP=run.py"
6) run "flask run"


### Disabling/Enabling certain features:
Since we won't enable all features at once, there is an object in app.config.py file called ENABLE_FEATURE where you can disable any of the features by setting its value to 0 and enable it by setting its value to 1.   


### Next Steps:
1) Automated tests - not sure if i should have a separate db for this
2) Integrate lcs slack endpoint
3) Set up a virtual env
