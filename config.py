import os
basedirectory=os.path.abspath(os.path.dirname(__file__))


class Config(object):
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'dhundh-ke-dikhao-to-mane'
	SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URI') or 'sqlite:///' + os.path.join(basedirectory,'gem.db')
	SQLALCHEMY_TRACK_MODIFICATIONS=False