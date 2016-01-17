import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension

# Base directory
basedir = os.path.abspath(os.path.dirname(__file__))

APPLICATION_NAME = "Restaurant Menu Application"
UPLOAD_FOLDER = os.path.join(basedir, 'uploads')

# Create my Flask app
app = Flask(__name__)

app.secret_key = 'b\'\xf4\x93v\xab~0n-#"\x19\x19Dy\xca\x14\xb3\x82`\xb6\xce\x11b"'
app.debug = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Connect to Database and create database session
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:////' + os.path.join(basedir, 'restaurantmenuwithusers.db')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# To disable the debugbar's interception
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

db = SQLAlchemy(app)

# enable debugtoolbar
toolbar = DebugToolbarExtension(app)

#  The view module has to be imported after the application object is created.
import views
