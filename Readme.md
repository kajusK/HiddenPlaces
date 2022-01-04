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

# Running the app
* Install the requirements `pip install -r requirements.txt`
* Configure `.env` file as described below
* Initialize database `flask db upgrade`
* Create a new admin user `flask user add-root foo@bar.org John Wick`
* Run `flask run` to launch the app

## Environmental variables
### Required
* **DATABASE_URL** Database connection as `dialect://username:password@host:port/database`, e.g. `sqlite:////tmp/database.sqlite` or `mysql://username:password@server/database`
* **SECRET_KEY** Random long string, it's used to encrypt sessions, tokens,...

## Optional
* **MAIL_SERVER** SMTP server address for mail sending
* **MAIL_PORT** Port to talk to SMTP server over
* **MAIL_USERNAME** User for the SMTP server
* **MAIL_PASSWORD** Password for the SMTP server

# Contributing
* [Flask intro and best practises](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world)
* Follow [PEP8 Code style](https://pep8.org/)
* Use [Google docstring format](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
* Don't use relative imports, use full package name
* Use python [typing](https://www.pythonsheets.com/notes/python-typing.html) where possible
* Write tests, validate generated HTML data and keep eye on amount of requests to the database per endpoint
* Run `make tests` to verify formatting, linting,...

## Preparing development environment
* create venv `python3 -m venv venv`
* ativate by `source venv/bin/activate` (every time you open terminal)
* Install requirements `pip install -r requirements.txt`
* Install requirements for tests `pip install -r tests/requirements.txt`
* Initialize database `flask db upgrade`
* Create a new admin user `flask user add-root foo@bar.org John Wick`
* Run the app `flask run`

## Database migrations
* The initial database migration table is set by `flask db init` and `flask db migrate`
* Once you change any of the sqlalchemy models, run
    `flask db migrate -m "Some change related message"`
* Run `flask db upgrade` to apply changes in the migration scripts
* Test and if everything works as expected, save the generated scripts into git

## Translations
* Translations are stored in `app/translations`, edit `messages.po` file
* Run `flask translate init <language_shortcut>` to create a new translation
* Run `flask translate update` to update list of translated strings when app changes
* Run `flask translate compile` to compile all translations after strings are translated
