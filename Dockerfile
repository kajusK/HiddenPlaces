FROM python:3

WORKDIR /project
ADD --chown=1000:1000 app /project/app
ADD --chown=1000:1000 .env run.py requirements.txt /project/
RUN pip install -r requirements.txt
CMD gunicorn run:app -w 2 --threads 2 -b 0.0.0.0:80