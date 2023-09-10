from flask import Blueprint, render_template, request, url_for, flash, session
from werkzeug.utils import redirect
from werkzeug.security import generate_password_hash, check_password_hash
from .. import db
from ..forms import RegisterForm, LoginForm
from ..models import Members
from datetime import datetime


bp=Blueprint('manage', __name__, url_prefix='/manage')

# 회원 리스트
@bp.route('/member_list')
def member_list():
    if session.get("user_id") != "manager":
        return redirect(url_for('main.hello'))
    member_list = Members.query.order_by(Members.create_date.desc())
    

    # 페이징
    page = request.args.get('page', type = int, default=1)
    member_list = member_list.paginate(page, per_page = 20)
    return render_template('manage/list.html', member_list = member_list)


# 계정 전환 
@bp.route('/transform/<member_id>')
def transform(member_id):
    if session.get("user_id") != "manager":
        return redirect(url_for('main.hello'))

    user = Members.query.filter_by(user_id=member_id).first()

    session.clear()
    session.clear()
    session['user_id']=user.user_id
    session['user_name']=user.user_name
    session['user_type']=user.user_type
    session['id'] = user.id

    return redirect(url_for('notice._list'))

# 승인 여부 변경
@bp.route('/permit/<member_id>')
def permit(member_id):
    user = Members.query.filter_by(user_id=member_id).first()

    if user.permit == 0 :
        user.permit = 1
        db.session.commit()
    elif user.permit == 1:
        user.permit = 0
        db.session.commit()
    
    return redirect(url_for('manage.member_list'))