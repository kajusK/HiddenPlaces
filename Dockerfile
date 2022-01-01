FROM python:3

WORKDIR /project
ENV FLASK_APP 'app'
ENV FLASK_ENV 'production'

ADD --chown=1000:1000 app /project/app
ADD --chown=1000:1000 migrations /project/migrations
ADD --chown=1000:1000 requirements.txt /project/
RUN pip install -r requirements.txt

EXPOSE 80
CMD flask db upgrade && gunicorn 'app:create_app()' -w 2 --threads 2 -b 0.0.0.0:80
