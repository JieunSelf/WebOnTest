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


    # 응시한 시험인 경우? -> 체크 표시..?

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
        # test_list = TestSet.query.all()
        # return render_template('/exam/list.html', test_list = test_list)
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


'''
이미지 한개만 업로드(old_Ver)
@bp.route('/detail/<test_id>', methods=['GET', 'POST'])
def detail(test_id):
    form = AnswerForm()
    test_set = TestSet.query.get(test_id)
    content = test_set.content.replace("\r\n", "<br />")
    content = Markup(content)
    if test_set.image_data :
        global image 
        image = b64encode(test_set.image_data).decode("utf-8")
    else :
        default_image = ImageTest.query.get(2)
        image = b64encode(default_image.data).decode("utf-8")

    tests2 = Test2.query.filter(Test2.test_id==test_id).order_by(Test2.number).all()
    user_id = session.get("user_id")
    u_id = session.get("id")

    # 답안 중복 제출 확인
    saved_answer_list = []
    for test in tests2:
        saved_answer = AnswerSet.query.filter(and_(AnswerSet.test2_id==test.id, AnswerSet.member_id == user_id)).first()
        if saved_answer :
            saved_answer_list.append(saved_answer)
    print(saved_answer_list)
    if user_id is None:
        return redirect(url_for('auth.login'))

    if saved_answer_list != []:
        flash('이미 응시한 시험입니다.')
        # test_list = TestSet.query.all()
        # return render_template('/exam/list.html', test_list = test_list)
        return redirect(url_for('exam._list'))

    if request.method == 'POST' and form.validate_on_submit():
        f = form.image.data
        if f :
            if allowed_file(f.filename):            
                filename = secure_filename(f.filename)
                image = f
                test_answer = TestAnswer(testset_id = test_id, member_id = u_id, file_name = filename, file_image = image.read(), create_date=datetime.now(), mimetype = f.mimetype)
                db.session.add(test_answer)
                db.session.commit()
            else :
                flash('이미지 파일만 가능합니다.')
                return redirect(request.url)

        answer_id=request.form.getlist('answer_id')
        answer=request.form.getlist('answer')
        for i in range(len(answer_id)):
            print(answer_id[i], answer[i])
            answer_save = AnswerSet(test2_id = answer_id[i], member_id = user_id, answer = answer[i], create_date = datetime.now())
            if saved_answer_list != []:
                for saved_answer in saved_answer_list:
                    db.session.delete(saved_answer)
            db.session.add(answer_save)
        test_set.exam_count +=1
        db.session.commit()

        return redirect(url_for('exam._list'))

        # 이미지 파일 저장
        # if form.image.data :
        #     if allowed_file(form.image.data.filename):            
        #         filename = secure_filename(form.image.data.filename)
        #         image = form.image.data
        #         print(filename, image)
        #         test_answer = TestAnswer(testset_id = test_id, member_id = u_id, file_name = filename, file_image = image.read(), create_date=datetime.now())
        #         db.session.add(test_answer)
        #         db.session.commit()
        #     else :
        #         flash('이미지 파일만 가능합니다.')
        #         return redirect(request.url)
        
        # return redirect(url_for('exam._list'))
    return render_template('/exam/detail.html', test_set = test_set, tests2 = tests2, form=form, image=image, content=content)
'''

