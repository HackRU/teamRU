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