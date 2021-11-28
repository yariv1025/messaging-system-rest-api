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
  
* Complete MongoDB URI should look like:   f'mongodb+srv://{username}:{password}{mongo_uri}'
##### Attention:    You must change MONGO_USER, MONGO_PASS, YOURS-PATH, etc. variables.

___


### Execute requests using Postman:
* Open Postman
* Create API collection
* Create the next CRUD requests:
    > * POST:
    >  * Create a new user | WEB_ROUTE/user <br>
    >    * Body fields: first_name, last_name, email, password <br>
    >    * Response: <br>
    >        * Status: 201 <br>
    >        * Body: <br>
                * id: <>
                * first_name: <>
                * last_name: <>
                * email: <>
                * password: <>
                * created_at: <>
                * last_login: <>
 
    >  * Login | WEB_ROUTE/login <br>
    >    * Body fields: email, password <br>
    >    * Response: <br>
    >        * Status: 200 <br>
    >        * Body:
                * status: <>
                * message: <>
                * access_token: <>
                * refresh_token: <>
  
    >  * Logout | WEB_ROUTE/oauth/logout <br>
    >    * Authorization Bearer Token filed: access_token <br>
    >    * Response: <br>
    >        * Status: 200 <br>
    >        * Body:
                * message: <>

    >  * Refresh access token | WEB_ROUTE/oauth/refresh <br>
    >    * Authorization Bearer Token filed: access_token. <br>
    >    * Body: <br>
    >       * key: grant_type, value: refresh_token <br>
    >       * key: refresh_token, value: refresh_token <br>
    >     * Response: <br>
    >        * Status: 200 <br>
    >        * Body:
                * user_id: <>
                * email: <>
                * exp: <>
                * new_access_token: <>
  
    >  * Write message | WEB_ROUTE/messages <br>
    >    * Authorization Bearer Token filed: access_token. <br>
    >    * Body fields: <br>
    >      * key: sender, value: sender <br>
    >      * key: receiver, value: receiver <br>
    >      * key: subject, value: subject <br>
    >      * key: message, value: message <br>
    >    * Response: <br>
    >        * Status: 201 <br>
    >        * Body:
                * message_id: <>
  
  > * GET: <br>
    >   * Get all messages | WEB_ROUTE/messages <br>
    >   * Authorization Bearer Token filed: access_token. <br>
    >   * Response: <br>
    >       * Status: 200 <br>
    >       * Body:
                * message_id: <>
                * sender_id: <>
                * sender_name: <>
                * receiver_name: <>
                * subject: <>
                * message: <>
                * created_at: <>
                * is_read: <>
  
    >   * Get message by id | WEB_ROUTE/messages/<message_id> <br>
    >   * Authorization Bearer Token filed: access_token. <br>
    >   * Response: <br>
    >       * Status: 200 <br>
    >       * Body:
                * message_id: <>
                * sender_id: <>
                * sender_name: <>
                * receiver_name: <>
                * subject: <>
                * message: <>
                * created_at: <>
                * is_read: <>
  
  > * DELETE:
    >  * Delete message | WEB_ROUTE/messages/<message_id> <br>
    >  * Authorization Bearer Token filed: access_token. <br>
    >  * Response: <br>
    >      * Status: 200 <br>
    >      * Body: number of deleted messages
  

[comment]: <> (![img.png]&#40;img.png&#41;)

###### * You can check your requests on [Heroku demo server](https://restmessagingsystem.herokuapp.com/)
###### * "Seed" data could be found in the next path: "YOUR_PROJECT_PATH/api/static/INIT_DATA.json".
  