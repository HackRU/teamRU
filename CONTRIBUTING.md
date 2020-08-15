### How to Setup Local MongoDB Instance
1. Follow the steps [here](https://docs.mongodb.com/manual/installation/) to install mongo for your respective OS
2. run `mongo --version` if you have installed mongo correctly then the output of this command will be your current mongo version
3. So there are two mains ways of interfacing with mongodb: 
    1. CLI (terminal)
    2. Mongo Compass (Desktop App) 
    > *We personally recommend Mongo Compass for beginners*

4. **CLI**
   Run the following commands inside of your computer's terminal
    1. `mongo` 
    2. `use <name_of_database>` this will be the name of your new mongo database
    3. `db.teams.insertOne({})` insert a collection called **teams** which will hold our teams info
    4. `db.users.insertOne({})` insert a collection called **users** which will hold our users info
    5. Create a file called `config.py` inside of `/src/flaskapp/` folder
    6. Copy the contents of `config.example.py` into `config.py`
    7. Insert `mongodb://127.0.0.1:27017/<name_of_database>` in the `DB_URI` field inside of `config.py` 

5. **Mongo Compass**
    1. Go to [here](https://www.mongodb.com/try/download/compass) to download Mongo Compass
    2. Click `connect` - *hostname: localhost and port: 27010*
    3. Click `Create Database` 
       1. Database Name: `<name_of_database>` 
       2. Collection Name: `teams`
       3. Click `Create Database`
    4. Click on your database in the list
    5. Click `Create Collection`
       1. Collection Name: `users`
    6.  Create a file called `config.py` inside of `/src/flaskapp/` folder
    7.  Copy the contents of `config.example.py` into `config.py`
    8.  Insert `mongodb://127.0.0.1:27017/<name_of_database>` in the `DB_URI` field inside of `config.py` 


## Styling and Documentation

In the long term, we want to make sure that code is properly styled and commented to make it easier for developers to maintain and enhance.

**Styling**

To achieve this on our current codebase, we will use a combination of pylint and black.

[pylint](https://www.pylint.org/)
- Useful for identifying issues such as import order, naming conventions, missing docstrings, etc.
- Doesn't actually make any changes, but provides a list of suggestions that can be made to improve the code
- All pylint codes can be found [here](http://pylint-messages.wikidot.com/all-codes)

[black](https://black.readthedocs.io/en/stable/)
- Aggressive but useful for creating standardized code styling
- Automatically fixes issues such as files ending without newlines, single quotes instead of double quotes, trailing whitespace, etc.

In these instances where we feel like ignoring pylint warnings, or where pylint and black disagree, we will suppress pylint. These issues will be handled on a case-by-case basis.

**Comments/Documentation**

In general, [Google's Python Style Guide](https://google.github.io/styleguide/pyguide.html) is a great resource. Specifically, we will be using their guidelines on [comments and docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) to document our code. Again, this isn't set in stone - any disagreement with the styling conventions can be handled on a case-by-case basis.

**Workflow**

In general, the developer workflow should look a little like this:

```
write code
run black
run pylint
while pylint raises warnings:
    for warning in warnings:
        if warning is important:
            fix it
        else:
            suppress it
    run pylint
run black
push code
```
