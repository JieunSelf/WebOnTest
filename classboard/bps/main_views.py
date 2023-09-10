'''
첫 페이지/로그인 리다이렉트
2021-05-24
'''
from flask import Blueprint, render_template, url_for, session
from werkzeug.utils import redirect

bp=Blueprint('main', __name__, url_prefix='/')
@bp.route('/')
def hello():
    user_id = session.get("user_id")
    if user_id == None:
        return redirect(url_for('auth.login'))
    else :
        return redirect(url_for('notice._list'))


