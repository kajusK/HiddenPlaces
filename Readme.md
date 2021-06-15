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
