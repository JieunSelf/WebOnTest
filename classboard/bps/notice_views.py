'''
공지사항
2021-05-24
'''
from flask import Blueprint, render_template, url_for, session, g, request, flash
from werkzeug.utils import redirect
from ..models import Notice, Members
from ..forms import CreateForm
from datetime import datetime
from .. import db

bp=Blueprint('notice', __name__, url_prefix='/notice')

@bp.route('/list')
def _list():
    #user_id = session.get("user_id")
    if session.get("user_id") == None:
        return redirect(url_for('auth.login'))
    notice_list = Notice.query.order_by(Notice.create_date.desc())

    page = request.args.get('page', type = int, default=1)
    notice_list = notice_list.paginate(page, per_page = 10)
    return render_template('notice/list.html', notice_list = notice_list)

@bp.route('/create/', methods=['GET', 'POST'])
def create():
    form = CreateForm()
    user_id = session.get("user_id")
    if user_id == None:
        return redirect(url_for('auth.login'))
    if request.method == 'POST' and form.validate_on_submit():
        member_id = session['id']
        notice = Notice(title=form.title.data, content = form.content.data, create_date=datetime.now(), member_id = member_id)
        db.session.add(notice)
        db.session.commit()
        return redirect(url_for('notice._list'))
    return render_template('notice/create.html', form=form)

from flask import Markup
@bp.route('/detail/<int:notice_id>/')
def detail(notice_id):
    user_id = session.get('user_id')
    notice = Notice.query.get(notice_id)
    content = notice.content.replace("\r\n", "<br />")
    content = Markup(content)
    notice.view_count += 1
    db.session.commit()
    return render_template('/notice/detail.html', notice=notice, content=content, user_id=user_id)


@bp.route('/modify/<int:notice_id>', methods=('GET', 'POST'))
def modify(notice_id):
    notice = Notice.query.get(notice_id)
    user_id = session.get("user_id")
    if user_id == None:
        return redirect(url_for('auth.login'))
    if user_id != notice.member.user_id:
        flash('수정 권한이 없습니다.')
        return redirect(url_for('notice.detail', notice_id = notice_id))

    if request.method == 'POST':
        form = CreateForm()
        if form.validate_on_submit():
            form.populate_obj(notice)  
            notice.modify_date = datetime.now() # 수정일시 저장
            db.session.commit()
            return redirect(url_for('notice.detail', notice_id = notice_id))
 
    form = CreateForm(obj= notice)

    return render_template('notice/create.html', form= form, user_id = user_id)

@bp.route('/delete/<notice_id>')
def delete(notice_id):
    notice = Notice.query.get(notice_id)
    user_id = session.get("user_id")
    if user_id != notice.member.user_id :
        flash('삭제권한이 없습니다')
        return redirect(url_for('notice.detail', notice_id = notice_id))
    db.session.delete(notice)
    db.session.commit()
    return redirect(url_for('notice._list'))

