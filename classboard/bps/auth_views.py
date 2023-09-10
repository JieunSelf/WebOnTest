'''
회원가입, 로그인
2021-05-24
'''
from flask import Blueprint, render_template, request, url_for, flash, session, g
from werkzeug.utils import redirect
from werkzeug.security import generate_password_hash, check_password_hash
from .. import db
from ..forms import RegisterForm, LoginForm
from ..models import Members, Test_Member, TestSet
from datetime import datetime


bp=Blueprint('auth', __name__, url_prefix='/auth')


#회원가입
@bp.route('/signup/', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    if request.method=='POST' and form.validate_on_submit():
        idn = (form.idn.data).strip()

        user = Members.query.filter_by(user_id=idn).first()
        if user:
            flash("이미 존재하는 아이디입니다.")
            return render_template('auth/signup.html', form=form)
        elif form.password1.data != form.password2.data :
            flash("비밀번호가 일치하지 않습니다.")
            return render_template('auth/signup.html', form=form)

        member = Members(user_id=idn, user_pw=generate_password_hash(form.password1.data), user_name=form.name.data, 
        user_type=form.usertype.data, create_date=datetime.now())
        db.session.add(member)

        db.session.commit()
        return redirect(url_for('main.hello'))
    return render_template('auth/signup.html', form = form)

#로그인
@bp.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Members.query.filter_by(user_id=form.userid.data).first()
        if (not user) or (user.is_activate == 1):
            flash("존재하지 않거나 탈퇴한 사용자입니다.")
            return render_template('auth/login.html', form=form)
        elif not check_password_hash(user.user_pw, form.password.data):
            flash("잘못된 비밀번호입니다.")
            return render_template('auth/login.html', form=form)
            # return render_template('auth/login.html', form=form)

        if user.permit == 1 :
            flash('관리자의 로그인 승인을 받아야 접속 가능합니다.')
            return render_template('auth/login.html', form=form)

        else:
            session.clear()
            session['user_id']=user.user_id
            session['user_name']=user.user_name
            session['user_type']=user.user_type
            session['id'] = user.id

            user.connect_date = datetime.now()
            db.session.commit()

            return redirect(url_for('notice._list'))
    return render_template('auth/login.html', form=form)

#로그아웃
@bp.route('/logout/')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

#회원정보 수정
@bp.route('/myinfo/<user_id>', methods=['GET', 'POST'])
def myinfo(user_id):
    form = RegisterForm()
    user = Members.query.filter(Members.user_id==user_id).first()

    if request.method=='POST':
        if form.password1.data != form.password2.data :
            flash("비밀번호가 일치하지 않습니다.")
            return redirect(request.url)
        # form = RegisterForm()
        # if form.validate_on_submit():
        user.user_pw = generate_password_hash(form.password1.data)
        user.user_name = form.name.data
        db.session.commit()
        session['user_name']=user.user_name
        return redirect(url_for('notice._list'))
        
    return render_template('/auth/myinfo.html', user=user, form=form)

#회원 탈퇴 기능
@bp.route('/delete_id/<user_id>', methods=['GET'])
def delete_id(user_id):
    user=Members.query.get(user_id)
    user.is_activate = 1
    db.session.commit()

    return redirect(url_for('auth.logout'))



# @bp.before_app_request
def load_logged_in_user():
    userid = session['user_id']
    # user_id = session.get('user_id')
    if userid is None:
        g.user = None
    else:
        g.user = Members.query.get(userid)