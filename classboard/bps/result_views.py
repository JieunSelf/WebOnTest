'''
결과보기 탭 관련
2021-05-24
'''
from re import S
from flask import Blueprint, render_template, url_for, session, request
from flask.wrappers import Response
from markupsafe import Markup

from werkzeug.utils import redirect
from ..models import AnswerSet, TestSet, Test2, Members, ScoreSet, ImageTest
from datetime import datetime
from .. import db
from sqlalchemy import and_

bp = Blueprint('result', __name__, url_prefix='/result')


@bp.route('/')
def index():
    user_id = session.get("user_id")
    if user_id == None:
        return redirect(url_for('auth.login'))
    
    member = Members.query.filter(Members.user_id==user_id).first()
    
    score_list = ScoreSet.query.filter(ScoreSet.member_id==member.id).all()
    score_openlist = []
    for score in score_list :
        if score.score_open == 1:
            score_openlist.append(score)

    return render_template('/result/index.html', score_openlist = score_openlist)

from flask import send_file
import numpy as np
from PIL import ImageFont, ImageDraw, Image
import cv2
import os
from io import BytesIO
from base64 import b64encode
@bp.route('/certificate/<course>/<grade>')
def certificate(course, grade):
    cert_img = os.path.dirname(os.path.dirname(__file__)) +"\static\certificate2.png"
    image = Image.open(cert_img)

    font1 = ImageFont.truetype(os.path.dirname(os.path.dirname(__file__))+"\\static\\fonts\\NanumMyeongjo-Bold.ttf", 28)
    font2 = ImageFont.truetype(os.path.dirname(os.path.dirname(__file__))+"\\static\\fonts\\NanumMyeongjo-Bold.ttf", 20)

    draw = ImageDraw.Draw(image)
    name = session.get("user_name")
    draw.text((315,425), name, font=font1, fill=(0,0,0))
    # course = course
    draw.text((315,499), course, font=font2, fill=(0,0,0))
    # grade = "100"
    draw.text((350,560), grade, font=font1, fill=(0,0,0))
    
    date = datetime.now()
    date = str(date.year)+'. '+str(date.month)+'. '+str(date.day)+'.'
    draw.text((380,970), date, font=font1, fill=(0,0,0))
    nd_image = np.array(image)

    load = os.path.dirname(os.path.dirname(__file__)) + "\static\kew.png"
    new_img = Image.fromarray(nd_image)
    new_img.save(load)

    return send_file(load, attachment_filename='certificate.png', mimetype='image/png')
    
    
@bp.route('/paper/<course>/<grade>')    
def paper(course, grade):
    cert_img = os.path.dirname(os.path.dirname(__file__)) +"\static\certificate2.png"
    image = Image.open(cert_img)

    font1 = ImageFont.truetype(os.path.dirname(os.path.dirname(__file__))+"\\static\\fonts\\NanumMyeongjo-Bold.ttf", 28)
    font2 = ImageFont.truetype(os.path.dirname(os.path.dirname(__file__))+"\\static\\fonts\\NanumMyeongjo-Bold.ttf", 20)

    draw = ImageDraw.Draw(image)
    name = session.get("user_name")
    draw.text((315,425), name, font=font1, fill=(0,0,0))
    # course = course
    draw.text((315,499), course, font=font2, fill=(0,0,0))
    # grade = "100"
    draw.text((350,560), grade, font=font1, fill=(0,0,0))
    
    date = datetime.now()
    date = str(date.year)+'. '+str(date.month)+'. '+str(date.day)+'.'
    draw.text((380,970), date, font=font1, fill=(0,0,0))
    nd_image = np.array(image)

    load = os.path.dirname(os.path.dirname(__file__)) + "\static\kew.png"
    new_img = Image.fromarray(nd_image)
    new_img.save(load)


@bp.route('/my_score_detail/<testset_id>')
def my_score_detail(testset_id):

    user_id = session.get('user_id')
    if user_id == None:
        return redirect(url_for('auth.login'))

    scoreset = ScoreSet.query.filter(and_(ScoreSet.testset_id==testset_id, ScoreSet.member_id==session.get('id'))).first()
    
    # 시험 문항
    test2 = Test2.query.filter(Test2.test_id==testset_id).all()

    # 응시자 답안
    answers = []
    # answer 개체 
    for test in test2:
        answer_set = AnswerSet.query.filter(and_(AnswerSet.test2_id==test.id, AnswerSet.member_id==user_id)).first()
        answers.append(answer_set)

    return render_template('/result/my_score_detail.html', scoreset=scoreset, test2=test2, answers=answers)