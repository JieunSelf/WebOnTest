'''
시험응시 탭 관련
2021-05-24
'''
from flask import Blueprint, render_template, url_for, session, g, request, flash
from werkzeug.utils import redirect
from ..models import Members, TestSet, Test2, AnswerSet, TestAnswer, ImageTest, Test_Member
from ..forms import AnswerForm
from datetime import datetime
from .. import db
from sqlalchemy import and_

bp=Blueprint('exam', __name__, url_prefix='/exam')

@bp.route('/list')
def _list():
    user_id = session.get("user_id")
    user_idn = session.get('id')
    if user_id == None:
        return redirect(url_for('auth.login'))

    # test_list = Test_Member.query.filter(and_( Test_Member.member_id==user_idn, Test_Member.select==1)).filter(TestSet.test_open=='1').order_by(TestSet.create_date.desc()).all()

    test_list = TestSet.query.filter(TestSet.test_open==1).order_by(TestSet.create_date.desc()).all()

    return render_template('/exam/list.html', test_list = test_list)





from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

from base64 import b64encode
from flask import Markup

@bp.route('/detail/<test_id>', methods=['GET', 'POST'])
def detail(test_id):
    form = AnswerForm()
    test_set = TestSet.query.get(test_id)
    content = test_set.content.replace("\r\n", "<br />")
    content = Markup(content)
    tests2 = Test2.query.filter(Test2.test_id==test_id).order_by(Test2.number).all()
    user_id = session.get("user_id")
    if user_id is None:
        return redirect(url_for('auth.login'))
    
    # 답안 중복 제출 확인
    saved_answer_list = []
    for test in tests2:
        saved_answer = AnswerSet.query.filter(and_(AnswerSet.test2_id==test.id, AnswerSet.member_id == user_id)).first()
        if saved_answer :
            saved_answer_list.append(saved_answer)

    if saved_answer_list != []:
        flash('이미 응시한 시험입니다.')
        return redirect(url_for('exam._list'))

    if request.method == 'POST' and form.validate_on_submit():
        answer_id=request.form.getlist('answer_id')
        answer=request.form.getlist('answer')
        img = request.files.getlist("image")
        print(img[0].content_type)

        if saved_answer_list != []:
            for saved_answer in saved_answer_list:
                db.session.delete(saved_answer)

        for i in range(len(answer_id)):
            if img[i] :
                if allowed_file(img[i].filename):
                    filename = secure_filename(img[i].filename)
                    file_image = img[i]
                    answer_save = AnswerSet(test2_id = answer_id[i], member_id = user_id, answer = answer[i], create_date = datetime.now(), img_name = filename, img_file = img[i].read(), mimetype=img[i].mimetype)
                else :
                    flash('이미지 파일만 가능합니다.')
                    return redirect(request.url)
            else : 
                answer_save = AnswerSet(test2_id = answer_id[i], member_id = user_id, answer = answer[i], create_date = datetime.now())
            db.session.add(answer_save)
        test_set.exam_count +=1
        db.session.commit()
        return redirect(url_for('exam._list'))

    return render_template('/exam/detail.html', test_set = test_set, tests2 = tests2, form=form, content=content)