from flask import Flask
from flask.ext.bcrypt import Bcrypt
from flask.ext.session import Session
from flask.ext.sqlalchemy import SQLAlchemy
from flask_googlemaps import GoogleMaps

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)


app.secret_key = 'super secret string'
bcrypt = Bcrypt(app)
Session(app)
GoogleMaps(app)



from curiosus import models, views
from curiosus.models import User
