import os

basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

WTF_CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'


SESSION_COOKIE_NAME = 'session'
PERMANENT_SESSION_LIFETIME = 3600
SESSION_TYPE = 'filesystem'
SESSION_USE_SIGNER = True


GOOGLEMAPS_KEY = 'AIzaSyCtJN3gcZGzNHENrgeIyMFyULn6UAK3Oyc'
