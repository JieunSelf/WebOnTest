# 채점하기 탭 관련

from flask import Blueprint, render_template, url_for, session, request, flash
from flask.helpers import send_file

from werkzeug.utils import redirect
from ..models import TestSet, Test2, AnswerSet, Members, ScoreSet, TestAnswer, ImageTest
from ..forms import ScoreForm
from datetime import datetime
from .. import db
from sqlalchemy import and_
import os


bp = Blueprint('score', __name__, url_prefix='/score')


@bp.route('/')
def index():
    user_id = session.get("user_id")
    if user_id == None:
        return redirect(url_for('auth.login'))

    if user_id == 'manager':
        test_list = TestSet.query.order_by(TestSet.create_date.desc()).all()
    else :
        test_list = TestSet.query.filter(TestSet.member_id==user_id).order_by(TestSet.create_date.desc()).all()
    return render_template('/score/index.html', test_list = test_list)

@bp.route('/list/<test_id>', methods=['GET', 'POST'])
def _list(test_id):
    user_id = session.get("user_id")
    # test_id = test_id
    if user_id == None:
        return redirect(url_for('auth.login'))

    test = TestSet.query.get(test_id)

    # 응시자 list
    ## 첫번째 문항 선택
    sortTest = Test2.query.filter(Test2.test_id==test_id).first()
    ## 첫번째 문항에 대한 답변 모두 선택
    sortAnswer = AnswerSet.query.filter(AnswerSet.test2_id==sortTest.id).all()
    ## 답변한 응시자 리스트 생성 (Members에서 이름 정보 추출)
    member_list = []
    score_list = []
    for Answer in sortAnswer:
        sortMember = Members.query.filter(Members.user_id == Answer.member_id).first()
        score_sum = ScoreSet.query.filter(and_(ScoreSet.testset_id==test_id, ScoreSet.member_id == sortMember.id)).first()
        if score_sum :
            score_list.append(score_sum)
        else :
            score_list.append(None)
        member_list.append(sortMember)

    score_sum = ScoreSet.query.filter(ScoreSet.testset_id == test_id).all()
    
    return render_template('/score/list.html', member_list = member_list, score_list = score_list, test_id = test_id, test=test)

@bp.route('/score_open/<score_id>')
def score_open(score_id):
    score = ScoreSet.query.filter(ScoreSet.id==score_id).first()
    if score :
        score.score_open = 1
        db.session.commit()
        return redirect(url_for('score._list', test_id =score.testset_id))
    else :
        flash('채점 결과가 없습니다.')
        return redirect(request.url)
    

@bp.route('/score_open_all/<testset_id>')
def score_open_all(testset_id):
    scores = ScoreSet.query.filter(ScoreSet.testset_id==testset_id).all()
    for score in scores :
        score.score_open = 1

    db.session.commit()
    return redirect(url_for('score._list', test_id =testset_id))


@bp.route('/score_close/<score_id>')
def score_close(score_id):
    score = ScoreSet.query.filter(ScoreSet.id==score_id).first()
    if score :
        score.score_open = 0
        db.session.commit()
    else :
        flash('채점 결과가 없습니다.')
    return redirect(url_for('score._list', test_id =score.testset_id))

@bp.route('/score_close_all/<testset_id>')
def score_close_all(testset_id):
    scores = ScoreSet.query.filter(ScoreSet.testset_id==testset_id).all()
    for score in scores :
        score.score_open = 0

    db.session.commit()
    return redirect(url_for('score._list', test_id =testset_id))


from io import BytesIO
from flask import Response
from base64 import b64encode
from flask import Markup
@bp.route('/detail/<test_id>/<member_id>', methods=['GET','POST'])
def detail(test_id, member_id):
    user_id=session.get("user_id")
    if user_id == None:
        return redirect(url_for('auth.login'))

    form = ScoreForm()
    test2 = Test2.query.filter(Test2.test_id==test_id).all()
    member = Members.query.filter(Members.id==member_id).first()

    answers = [] # answer 개체
    answer_list = {} # 답안
    img_list = {}
    score_list = []
    n=1
    for test in test2:
        answer_set = AnswerSet.query.filter(and_(AnswerSet.test2_id ==test.id, AnswerSet.member_id == member.user_id)).first()

        answers.append(answer_set)

        answer_content = answer_set.answer.replace("\r\n", "<br />")
        answer_content = Markup(answer_content)
        answer_list[n] = answer_content
        n+=1

        if answer_set.img_file : 
            global image
            image = b64encode(answer_set.img_file).decode("utf-8")
            img_list[n] = image
        else :
            default_image = ImageTest.query.get(1)
            image = b64encode(default_image.data).decode("utf-8")
            img_list[n] = image

        score_list.append(answer_set.score)

    if request.method == 'POST' and form.validate_on_submit():
        score = request.form.getlist('score')
        sum_score = 0
        print(score)
        for (i, j) in zip(score, answers):
            j.score = int(i)
            j.score_date = datetime.now()
            db.session.commit()
            sum_score += int(i)
        score_sum = ScoreSet(testset_id=test_id, member_id = member_id, score_sum = sum_score, create_date = datetime.now())

        saved_sum = ScoreSet.query.filter(and_(ScoreSet.testset_id==test_id, ScoreSet.member_id == member_id)).first()

        if saved_sum != None :
            db.session.delete(saved_sum)

        db.session.add(score_sum)
        db.session.commit()
        
        return redirect(url_for('score._list', test_id =test_id))

    return render_template('/score/detail.html', test2=test2, answer_list = answer_list, member = member, form=form,  score_list=score_list, img_list = img_list)


# 점수 csv파일 다운로드
from flask import send_file
import csv
@bp.route('/csv_download/<testset_id>')
def csv_download(testset_id):
    file_path = os.path.dirname(os.path.dirname(__file__)) +"\\static\\result.csv"

    testset = ScoreSet.query.filter(ScoreSet.testset_id==testset_id).all()
    members = []
    scores = []
    for test in testset :
        members.append(test.member.user_name)
        scores.append(test.score_sum)
    f = open(file_path, 'w', encoding='utf-8-sig', newline='')
    f.write("이름,점수"+'\n')
    for member, score in zip(members, scores):
        f.write(member + ',' + str(score) + '\n')
    f.close()

    return send_file(file_path, mimetype='text/csv', attachment_filename='result.csv', as_attachment=True)

# 학생들의 답안 다운로드
@bp.route('/result_download/<testset_id>')
def result_download(testset_id):
    user_id=session.get("user_id")
    if user_id == None:
        return redirect(url_for('auth.login'))

    testset = TestSet.query.get(testset_id)
    tests = testset.tests_2 # test 문항
    answers = [i.answers for i in tests] # 각 테스트 문항의 답안

    answer_dict = {}
    member_list = [i.member_id for i in answers[0]]
    # answer_dict { 'member_id':[answer...], }
    for member in member_list:
        answer_dict[member] = []
        answer_dict[member] = [AnswerSet.query.filter(and_(AnswerSet.test2_id==i.id, AnswerSet.member_id==member)).first() for i in tests]

    return render_template('/score/result_download.html', answer_dict=answer_dict)