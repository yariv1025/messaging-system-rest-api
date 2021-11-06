## Messaging System REST API (Backend)

> ### Requirements:
> * Python 3.7
> * MongoDB
___

### Run the app:
#### 1) Clone the project:
```shell
git clone git@github.com:yariv1025/messaging-system-rest-api.git
```
#### 2) Edit configuration:
>* Install pipenv 
>* Install all dependencies from pipfile

#### 3) Edit configuration:
>* Add new configuration:
>    * Press + button  
>       * Python
>           * name: APP
>           * Script path: "YOURS-PATH"\messaging-system-rest-api\src\app.py
>           * Environment variables: ;FLASK_ENV=development;FLASK_APP=./src/app.py;MONGO_USER="YOURS-USERNAME";MONGO_PASS="YOURS-PASSWORD";MONGO_URI="YOURS_DB_URI";SECRET_KEY="YOUR_SECRET_KEY"
  
*Complete mongo URI should look like: f'mongodb+srv://{username}:{password}{mongo_uri}'
###### Attention: You must change MONGO_USER, MONGO_PASS, YOURS-PATH, etc. variables.
___

### Execute requests using Postman(use the attached PDF file):
* First, seed your db with the seed route.
  <br>
>###### * "Seed" data could be found in "src/seed/INIT_DATA.json".
  