'''
Form 양식 처리
2021-05-24
'''
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, HiddenField, IntegerField, MultipleFileField
from wtforms.validators import DataRequired, EqualTo

from flask_wtf.file import FileField

class RegisterForm(FlaskForm):
    idn = StringField('아이디', validators=[DataRequired()])
    password1 = PasswordField('비밀번호', validators=[DataRequired()])
    password2 = PasswordField('비밀번호 확인', validators=[DataRequired()])
    name = StringField('이름', validators=[DataRequired()])
    usertype = SelectField('구분', choices=[('2', '학생'), ('1', '교사'), ('3', '학부모') ], validators=[DataRequired()])

class LoginForm(FlaskForm):
    # class UserPassword(object):
    #     def __init__(self, message=None):
    #         self.message = message
    #     def __call__(self, form, field):
    #         userid = form['userid'].data
    #         password = field.data

    #         member = Memberes.query.filter_by(userid=user_id).first()
    #         if member.password != user_pw:
    #             raise ValueError('Wrong Password!')
                
    userid = StringField('userid', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])

class CreateForm(FlaskForm):
    title = StringField('제목', validators=[DataRequired()])
    content = TextAreaField('내용',validators=[DataRequired()] )

class AnswerForm(FlaskForm):
    answer_id = HiddenField()
    answer = TextAreaField('답안', validators=[DataRequired('작성하지 않은 답안이 있습니다.')])
    image = MultipleFileField()

class ScoreForm(FlaskForm):
    score = IntegerField('점수', validators=[DataRequired('채점하지 않는 문항이 있습니다.')])

class TestForm(FlaskForm):
    test = TextAreaField('문항')
