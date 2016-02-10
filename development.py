import os

# Base directory
_basedir = os.path.abspath(os.path.dirname(__file__))

APPLICATION_NAME = "Restaurant Menu Application"

UPLOAD_FOLDER = os.path.join(_basedir, 'uploads')


SECRET_KEY = 'the-cake-is-a-lie'
DEBUG = True
MAX_CONTENT_LENGTH = 16 * 1024 * 1024

# Connect to Database and create database session
SQLALCHEMY_DATABASE_URI = 'sqlite:////' + os.path.join(_basedir, 'restaurantmenuwithusers.db')

SQLALCHEMY_TRACK_MODIFICATIONS = False

# To disable the debugbar's interception

DEBUG_TB_INTERCEPT_REDIRECTS = False

del os
