# Technical test

#### Setup

- Install python 3.7 & pipenv
- `pipenv install` to install project's requirements

#### Run

- `pipenv shell` to enter virtual environment (loading the variables in .env)
- `flask run`

#### Explore DB

Database is running on SQLite, it can be browsed using "DB Browser for SQLite" for instance

#### Expected work

1. Connect to La Poste API (https://developer.laposte.fr/)
2. Create an endpoint that fetch the status of a given letter on the La Poste API, and update it in the database
3. Create an endpoint that fetch the status of all letters on the La Poste API, and update it in the database
4. Make previous endpoint respond instantly, and launch an asynchronous task that update all the status

There is no need to do a front interface, you can just share a Postman collection to test it.

#### Bonus

- Unit, integration, E2E tests
- Store the status history of each letter in a new table
- Impress us


# Solution
 - External api lives in separate folder `/external`
 - Added new table to store all letter status
 - DB migration are stored in `/migrations` folder
 - Test are stored in `/test` folder and can be run via `pytest` command
 - Updating all letters in background is done via `ThreadPool`
 - App can be run locally via `flask run` or via Docker (don't forget to put your own API key into .env file)
 - Code is formatted by `black`, imports are sorted by `isort`
 - Postman endpoint collection can be found here:

    [![Run in Postman](https://run.pstmn.io/button.svg)](https://app.getpostman.com/run-collection/4055513-d57cb42f-4423-420c-8389-b77935e34462?action=collection%2Ffork&collection-url=entityId%3D4055513-d57cb42f-4423-420c-8389-b77935e34462%26entityType%3Dcollection%26workspaceId%3D40a24c94-43ed-4b8f-8763-0a53c38e03dc)
