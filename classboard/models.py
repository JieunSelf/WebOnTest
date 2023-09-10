'''
Sqlite DB 구조
2021-05-24
'''
from . import db

class Members(db.Model):
    __tablename__ = 'Members'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(200), nullable = False,  )
    user_pw = db.Column(db.String(250), nullable = False)
    user_name = db.Column(db.String(150), nullable = False)
    user_type = db.Column(db.String(100), nullable= False)
    create_date = db.Column(db.DateTime(), nullable=False)
    permit = db.Column(db.Integer, default = 1) #default=0인 경우 자동 승인
    connect_date = db.Column(db.DateTime()) # 마지막 접속시간
    is_activate = db.Column(db.Integer)  # 탈퇴여부
    # notice = db.relationship('Notice', backref='member')
    # def __init__(self, user_id, user_pw, user_name, user_type, create_date):
    #     self.user_id = user_id
    #     self.user_pw = user_pw
    #     self.user_name = user_name
    #     self.user_type = user_type
    #     self.create_date=create_date
    #ip 정보

class Notice(db.Model):
    __tablename__ = 'Notice'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable = False)

    content = db.Column(db.Text(), nullable=False)
    create_date = db.Column(db.DateTime(), nullable=False)

    member_id = db.Column(db.String, db.ForeignKey('Members.id'), nullable=False)
    member = db.relationship('Members', backref = db.backref('notice_set'))

    modify_date = db.Column(db.DateTime(), nullable=True)
    view_count = db.Column(db.Integer, default = 0)

class TestSet(db.Model):
    __tablename__ = 'TestSet'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable = False)

    content = db.Column(db.Text(), nullable=False)
    create_date = db.Column(db.DateTime(), nullable=False)

    member_id = db.Column(db.String, db.ForeignKey('Members.user_id'), nullable=False)
    member = db.relationship('Members', backref = db.backref('test_set'))

    modify_date = db.Column(db.DateTime(), nullable=True)

    # 이미지 추가
    image_name = db.Column(db.String(300))
    image_data = db.Column(db.LargeBinary)
    image_mimetype = db.Column(db.String(100))

    # 응시 인원 확인
    exam_count = db.Column(db.Integer, default = 0)

    # 점수 공개 여부 -> ??? score.score_open 과 중복됨! 삭제!!
    score_open = db.Column(db.Integer, default = 0)

    # 시험 공개 여부
    test_open = db.Column(db.Integer, server_default='0') 

#응시 가능한 학생 -> list로? 아니면 명단으로??
class Test_Member(db.Model):
    __tablename__ = 'Test_Member'
    id = db.Column(db.Integer, primary_key=True)

    test_id = db.Column(db.Integer, db.ForeignKey('TestSet.id', ondelete='CASCADE'), nullable=False)
    test_ = db.relationship('TestSet', backref = db.backref('test_mem', cascade='all, delete-orphan'))

    member_id = db.Column(db.Integer, db.ForeignKey('Members.id'), nullable=False)
    member = db.relationship('Members', backref = db.backref('test_on'))

    select = db.Column(db.Integer)


class Test2(db.Model):
    __tablename__ = 'Test2'
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('TestSet.id', ondelete='CASCADE'), nullable=False)
    test_ = db.relationship('TestSet', backref = db.backref('tests_2', cascade='all, delete-orphan'))
    # c.f. passive_deletes = True : 해당 TestSet이 삭제되어도 삭제되지 않는다.

    number = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text(), nullable=False)

    img_name = db.Column(db.String(300))
    img_file = db.Column(db.LargeBinary)
    mimetype = db.Column(db.String(100))


class AnswerSet(db.Model):
    __tablename__ = 'AnswerSet'
    id = db.Column(db.Integer, primary_key=True)
    test2_id = db.Column(db.Integer, db.ForeignKey('Test2.id', ondelete='CASCADE'), nullable=False)
    test2 = db.relationship('Test2', backref = db.backref('answers', cascade='all, delete-orphan'))

    member_id = db.Column(db.Integer, db.ForeignKey('Members.user_id'), nullable=False)
    member = db.relationship('Members', backref = db.backref('answers'))

    answer = db.Column(db.String, nullable=False)

    create_date = db.Column(db.DateTime(), nullable=False)

    score = db.Column(db.Integer)
    score_date = db.Column(db.DateTime())

    img_name = db.Column(db.String(300))
    img_file = db.Column(db.LargeBinary)
    mimetype = db.Column(db.String(100))

# 학생들이 사진 제출한 답안 테스트
class TestAnswer(db.Model):
    __tablename__ = 'TestAnswer'
    id = db.Column(db.Integer, primary_key= True)
    
    testset_id = db.Column(db.Integer, db.ForeignKey('TestSet.id', ondelete='CASCADE'), nullable=False)
    testset = db.relationship('TestSet', backref = db.backref('test_answer', cascade='all, delete-orphan'))

    member_id = db.Column(db.Integer, db.ForeignKey('Members.id'), nullable=False)
    member = db.relationship('Members', backref = db.backref('test_answer'))

    file_name = db.Column(db.String(300))
    file_image = db.Column(db.LargeBinary)

    create_date = db.Column(db.DateTime(), nullable=False)
    mimetype = db.Column(db.String(100))

class ScoreSet(db.Model):
    __tablename__ = 'ScoreSet'
    id = db.Column(db.Integer, primary_key=True)
    testset_id = db.Column(db.Integer, db.ForeignKey('TestSet.id', ondelete='CASCADE'))
    testset = db.relationship('TestSet', backref = db.backref('score_set', cascade='all, delete-orphan'))

    member_id = db.Column(db.Integer, db.ForeignKey('Members.id'), nullable=False)
    member = db.relationship('Members', backref = db.backref('score_set')) 

    score_sum = db.Column(db.Integer)
    create_date = db.Column(db.DateTime())

    score_open = db.Column(db.Integer, default = 0)

# 이미지를 저장하지 않은 학생 답안에 보여줄 이미지->제출된 이미지 파일이 없습니다.
class ImageTest(db.Model):
    __tablename__ = 'ImageTest'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300))
    # images = db.Column(db.BLOB)
    data = db.Column(db.LargeBinary)
    mimetype = db.Column(db.String(100))