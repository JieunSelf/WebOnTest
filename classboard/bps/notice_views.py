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
    # rows를 정의해야 함~~
    notice_list = Notice.query.order_by(Notice.create_date.desc())
    #.all() -> list : [] 공지사항이 없습니다..?

    # 페이징
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
        # notice = Notice(title=form.title.data, content = form.content.data, create_date=datetime.now(), member_id = g.user_id)
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
    # 로그인한 사용자와 공지글의 작성자가 다른 경우
    if user_id != notice.member.user_id:
        flash('수정 권한이 없습니다.')
        return redirect(url_for('notice.detail', notice_id = notice_id))

    if request.method == 'POST':
        #<공지 수정>을 하고 <저장하기>버튼을 눌렀을 경우
        form = CreateForm()
        if form.validate_on_submit():
            form.populate_obj(notice) # form 변수에 들어 있는 데이터(화면에 입력되어 있는 데이터)를 notice 객체에 적용해 준다. 
            notice.modify_date = datetime.now() # 수정일시 저장
            db.session.commit()
            return redirect(url_for('notice.detail', notice_id = notice_id))
    
        #<질문수정> 버튼을 눌렀을 때 = Get 방식으로 요청되는 경우! 
        #db에서 조회한 데이터를 템플릿에 바로 적용하는 가장 간단한 방법은, 조회한 데이터를 obj 매개변수에 전달하여 폼을 생성하는 것이다. 
    form = CreateForm(obj= notice)
        #CreateForm의 subject, content 필드에 notice 객체의 subject, content의 값이 적용된다!
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




'''
@bp.route('/detail/<int:question_id>/')
def detail(question_id):
    form = AnswerForm()
    #get_or_404 함수는 해당 데이터를 찾을 수 없는 경우에 404페이지를 출력해 준다.
    question = Question.query.get_or_404(question_id)
    return render_template('question/question_detail.html', question = question, form = form)
'''



