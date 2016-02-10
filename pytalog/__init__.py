from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension


# Create my Flask app
app = Flask(__name__)
app.config.from_object('development_config')

db = SQLAlchemy(app)

# enable debugtoolbar
toolbar = DebugToolbarExtension(app)

#  The view module has to be imported after the application object is created.
import views
