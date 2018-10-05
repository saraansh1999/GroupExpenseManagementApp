from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager


gem=Flask(__name__)
gem.config.from_object(Config)
db=SQLAlchemy(gem)
migrate=Migrate(gem,db)
login=LoginManager(gem)
login.login_view='login'



from gem import routes,models