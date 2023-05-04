from flask import Flask
import sass
from website.models import *
from website.views import views
from website.errorhandler import errorhandler

def create_app():
    sass.compile(dirname=('website/static/sass','website/static/css'))
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'not_important_rn_but_maybe_add_a_secure_one_later' #some random string here
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'

    db.init_app(app)

    #app.jinja_env.globals.update(some_global = some_global) #can be used for variables or functions

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(errorhandler, url_prefix='/')
    return app
