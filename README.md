## Messaging System REST API (Backend)

> ### Requirements:
> * Python 3.7
> * MongoDB
> * PyCharm IDE (recommended)
___

### Run the app:
#### 1) Clone the project:
```shell
git clone git@github.com:yariv1025/messaging-system-rest-api.git
```


#### 2) Install dependencies:
```shell
pip install pipenv            #Install pipenv and create the virtual environment
pipenv install                #Install packages
pipenv install all --dev      #Install all dev dependencies
pipenv lock                   #Generate a lockfile
```


#### 3) Create your MongoDB atlas cluster:
* Use [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) website to create your own database and cluster


#### 4) Edit configuration:
* Add new configuration:
    * Press + button  
       * Python
           * name: APP
           * Script path: "YOURS-PATH"\messaging-system-rest-api\src\app.py
           * Environment variables: ;FLASK_ENV=development;FLASK_APP=./src/app.py;MONGO_USER="YOURS-USERNAME";MONGO_PASS="YOURS-PASSWORD";MONGO_URI="YOURS_DB_URI";SECRET_KEY="YOUR_SECRET_KEY"
  
<font color="red">*</font> Complete MongoDB URI should look like:   f'mongodb+srv://{username}:{password}{mongo_uri}'
##### <font color="red"> Attention:</font> You must change MONGO_USER, MONGO_PASS, YOURS-PATH, etc. variables.
___


### Execute requests using Postman:
* Open Postman
* Create API collection
* Create the CRUD requests

###### <font color="red">*</font> You can check your requests on [Heroku demo server](https://restmessagingsystem.herokuapp.com/)
###### <font color="red">*</font> "Seed" data could be found in the next path: "YOUR_PROJECT_PATH/api/static/INIT_DATA.json".
  