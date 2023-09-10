'''
Flask 처음 실행할 때 블루프린트 등 처리하는 코드 
2021-05-24
'''

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

import config

db=SQLAlchemy()
migrate = Migrate()

# from .models import db

import os
from flask_wtf.csrf import CSRFProtect


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    #ORM
    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    #이 속성이 False라면 다음과 같은 '제약 조건의 변경을 지원하지 않는다'는 오류 발생

    from . import models

    # #데이터베이스 연결
    # app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:911210@localhost/webtest'
    # app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN']=True
    # app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

    SECRET_KEY = os.urandom(32)
    app.config['SECRET_KEY'] = SECRET_KEY

    csrf=CSRFProtect()
    csrf.init_app(app)


    #블루프린트 등록
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

    #진자 템플릿 업데이트
    from base64 import b64encode
    app.jinja_env.globals.update(
    zip=zip, 
    enumerate=enumerate, 
    b64encode=b64encode
)

    #필터
    from .filter import format_datetime
    app.jinja_env.filters['datetime'] = format_datetime

    return app

