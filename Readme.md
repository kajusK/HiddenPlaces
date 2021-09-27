# Hidden Places web database

![trunk](https://drone.dev.deadbadger.cz/api/badges/kajus/HiddenPlaces/status.svg)

This project is supposed to provide a database of various interesting object
in a web app form, e.g.
* abandoned mining objects
* unused underground facilities (shelters, WWII factories,...)
* abandoned buildings (houses, factories,...)
* and many more

As these objects gets heavily destroyed by vandals once publicly known, the
app contains a several layers of permissions based on users reputation.


## Running the app in docker
* Run `make image` to build a docker image `hidden_places`
* Run `docker run --name hidden_places -d hidden_places`, the app will be on port 80
* See the `.env` file for possible environmental variables, specifically the DB settings

## Running the app
* Install the requirements `pip install -r requirements.txt`
* Run `python run.py` to launch the app for debbugging/testing
* Run `make tests` to run the app tests


# Contributing
* [Flask intro and best practises](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins)
* [PEP8 Code style](https://pep8.org/)

## Preparing development environment
* create venv `python3 -m venv venv`
* ativate by `source venv/bin/activate` (every time you open terminal)
* Install requirements `pip install -r requirements.txt`
* Install requirements for tests `pip install -r tests/requirements.txt`
* Initialize database `flask db upgrade`
* Create a new admin user `flask user add-root foo@bar.org John Wick`

## Database migrations
* The initial database migration table is set by `flask db init` and `flask db migrate`
* Once you change any of the sqlalchemy models, run
    `flask db migrate -m "Some change related message"`
    (unable to work with name changes, edit generated files manually)
* Run `flask db upgrade` to apply changes in the migration scripts
* Test and if everything works as expected, save the generated scripts into git

## Rules
* Follow PEP8 code style (run `flake8` to verify)
* Don't use relative imports, use full package name
* Use python typing
* Use [Google docstring format](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
* Write tests, validate generated HTML data and keep eye on amount of requests to the database per endpoint
