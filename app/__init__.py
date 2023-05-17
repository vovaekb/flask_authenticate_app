import os
from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from app import models


app = Flask(__name__)

# the toolbar is only enabled in debug mode:
app.debug = True

app.config['SECRET_KEY'] = os.environ('SECRET_KEY') # 'Th1s1ss3cr3t'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

toolbar = DebugToolbarExtension(app)

from app import views