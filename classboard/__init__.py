from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

import config

db=SQLAlchemy()
migrate = Migrate()

import os
from flask_wtf.csrf import CSRFProtect


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    #ORM
    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)

    from . import models

    SECRET_KEY = os.urandom(32)
    app.config['SECRET_KEY'] = SECRET_KEY

    csrf=CSRFProtect()
    csrf.init_app(app)


    # blueprint
    from .bps import main_views, auth_views, notice_views, upload_views, exam_views, score_views, result_views, manage_views
    app.register_blueprint(main_views.bp)
    app.register_blueprint(auth_views.bp)
    app.register_blueprint(notice_views.bp)
    
    csrf.exempt(upload_views.bp)
    app.register_blueprint(upload_views.bp)
    
    app.register_blueprint(exam_views.bp)
    app.register_blueprint(score_views.bp)
    app.register_blueprint(result_views.bp)
    app.register_blueprint(manage_views.bp)

    from base64 import b64encode
    app.jinja_env.globals.update(
    zip=zip, 
    enumerate=enumerate, 
    b64encode=b64encode
)
    from .filter import format_datetime
    app.jinja_env.filters['datetime'] = format_datetime

    return app