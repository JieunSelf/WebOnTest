'''
시험업로드 탭 관련
2021-05-24
'''
from flask import Blueprint, render_template, url_for, session, g, request, flash
from werkzeug.datastructures import MIMEAccept
from werkzeug.utils import redirect
from ..models import Members, TestSet, Test2, ImageTest, Test_Member
from ..forms import CreateForm
from datetime import datetime
from .. import db
from sqlalchemy import and_
import json


bp=Blueprint('upload', __name__, url_prefix='/upload')

@bp.route('/list/<userid>')
def _list(userid):
    user_id = session.get("user_id")
    if user_id == None:
        return redirect(url_for('auth.login'))

    if user_id == 'manager':
        test_list = TestSet.query.order_by(TestSet.create_date.desc())
    else :
        test_list = TestSet.query.filter_by(member_id = userid).order_by(TestSet.create_date.desc())

    # 페이징
    page = request.args.get('page', type = int, default = 1)
    test_list = test_list.paginate(page, per_page = 6)
    print(test_list.items)

    return render_template('/upload/list.html', userid=userid, test_list = test_list)


from flask import Markup
@bp.route('/detail/<test_id>')
def detail(test_id):
    test_set = TestSet.query.get(test_id)
    content = test_set.content.replace("\r\n", "<br />")
    content = Markup(content)
    test = Test2.query.filter(Test2.test_id==test_id).order_by(Test2.number).all()
    
    user_id = session.get("user_id")
    if user_id == 'manager' :
        return render_template('/upload/detail.html', test_set = test_set, test = test, user_id = user_id, content=content)

    if user_id != test_set.member_id:
        flash('열람권한이 없습니다')
        return redirect(url_for('auth.login'))
    
    return render_template('/upload/detail.html', test_set = test_set, test = test, user_id = user_id, content=content)

@bp.route('/delete/<test_id>')
def delete(test_id):
    test_set = TestSet.query.get(test_id)
    test = Test2.query.filter(Test2.test_id==test_id).all()
    user_id = session.get("user_id")

    if user_id == 'manager':
        db.session.delete(test_set)
        for t in test :
            db.session.delete(t)
        db.session.commit()
        return redirect(url_for('upload._list', userid = user_id))

    if user_id != test_set.member_id :
        flash('삭제권한이 없습니다')
        return redirect(url_for('auth.login'))
    db.session.delete(test_set)
    for t in test:
        db.session.delete(t)
    db.session.commit()
    return redirect(url_for('upload._list', userid = user_id))

# 시험지 만들기
@bp.route('/test_step1', methods=['GET', 'POST'])
def test_step1():
    form = CreateForm()
    user_id = session.get("user_id")
    if user_id == None:
        return redirect(url_for('auth.login'))
    if request.method == 'POST' and form.validate_on_submit():
        testset = TestSet(title = form.title.data,  content = form.content.data, create_date = datetime.now(), member_id = user_id)
        db.session.add(testset)
        db.session.commit()
        # return redirect(url_for('upload.ajax_test', test_id = testset.id))
        return redirect(url_for('upload.test_step2', test_id = testset.id))
    return render_template('upload/test_step1.html', form = form)

from werkzeug.utils import secure_filename
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/test_step2/<test_id>', methods=['GET', 'POST'])
def test_step2(test_id):
    user_id = session.get("user_id")
    if user_id == None:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST' :
        testdata = request.form.getlist('testdata')
        
        img = request.files.getlist("image") 
        print(img)

        number = 1
        for i in range(len(testdata)):
            if testdata[i] == '':
                pass
            else :
                if img[i] :
                    if allowed_file(img[i].filename):
                        filename = secure_filename(img[i].filename)
                        test2 = Test2(test_id=test_id, number = number, content = testdata[i], img_file = img[i].read(), img_name = filename, mimetype = img[i].mimetype)
                        number+=1
                    else :
                        flash('이미지 파일만 가능합니다.')
                        return redirect(request.url)
                else :
                    test2 = Test2(test_id=test_id, number=number, content = testdata[i])
                    number+=1
                db.session.add(test2)
                db.session.commit()
        return redirect(url_for('upload._list', userid = user_id))
    return render_template('upload/test2.html')


@bp.route('/modify/step1/<test_id>', methods = ['GET', 'POST'])
def modify_1(test_id):
    testset = TestSet.query.get(test_id)
    user_id = session.get("user_id")
    if user_id != testset.member_id :
        flash('수정 권한이 없습니다.')
        return redirect(url_for('auth.login'))

    if testset.exam_count > 0 :
        flash('응시자가 있는 경우 수정할 수 없습니다.')
        return redirect(url_for('upload._list', userid = user_id))

    if request.method == 'POST':
        form=CreateForm()
        if form.validate_on_submit():
            form.populate_obj(testset)
            testset.modify_date = datetime.now()
            db.session.commit()
            return redirect(url_for('upload.modify_2', test_id = testset.id)) 

    form = CreateForm(obj=testset) 
    return render_template('upload/test_step1.html', form=form, modify=True)

@bp.route('/modify/step2/<test_id>', methods = ['GET', 'POST'])
def modify_2(test_id):
    user_id = session.get("user_id")
    if user_id == None:
        return redirect(url_for('auth.login'))

    # 기존 문항
    Tests = Test2.query.filter(Test2.test_id ==test_id).all()
    # 마지막 문항의 id
    last_test = Test2.query.order_by(Test2.id.desc()).first()
    print(last_test.id)
    #test_id_count = Test2.query.count()
    test_id_count = last_test.id

    if request.method == 'POST':
        # 새로 작성한 문항 {'id' : '문항', ...}
        modify_tests = request.form.to_dict()
        print(modify_tests)
        # 새로 첨부한 이미지 
        img = request.files.getlist("image")
        number = 1
        print(img[0].filename)


        for k, v, i in zip(modify_tests.keys(), modify_tests.values(), img):
            # 기존 문항
            saved_test = Test2.query.filter(Test2.id==int(k)).first()

            # 기존 문항 있으면
            if saved_test:
                # 문항 저장
                saved_test.content = v
                saved_test.number = number
                # 이미지 저장 - 업로드한 이미지 있으면 (없으면 기존 db 변경 없음)
                if i:
                    if allowed_file(i.filename):
                        filename = secure_filename(i.filename)
                    else :
                        flash('이미지 파일만 가능합니다.')
                        return redirect(request.url)
                        
                    saved_test.img_file = i.read()
                    saved_test.img_name = filename
                    saved_test.mimetype = i.mimetype
                db.session.commit()
                number +=1
            
            # 기존 문항 없으면
            else :
                # 업로드한 이미지 파일 있으면
                if i :
                    if allowed_file(i.filename):
                        filename = secure_filename(i.filename)

                        new_test = Test2(test_id=test_id, number = number, content = v, img_file = i.read(), img_name = filename, mimetype = i.mimetype)

                    else :
                        flash('이미지 파일만 가능합니다.')
                        return redirect(request.url)
                # 업로드한 이미지 파일 없으면
                else :
                    new_test = Test2(test_id=test_id, number=number, content=v)
                db.session.add(new_test)
                db.session.commit()
                number+=1
        count = len(img)

        for n in range(1, count+1):
            double_tests = Test2.query.filter(and_(Test2.test_id==test_id, Test2.number==n)).all()
            if len(double_tests)>1:
                db.session.delete(double_tests[0])
                db.session.commit()
            old_test = Test2.query.filter(and_(Test2.test_id == test_id, Test2.number>count)).first()
            if old_test:
                db.session.delete(old_test)
                db.session.commit()
        
        return redirect(url_for('upload._list', userid = user_id))


        
    return render_template('upload/test_step2_modify.html', Tests=Tests, test_id_count = json.dumps(test_id_count))



@bp.route('/open/<testset_id>')
def open(testset_id):
    userid = session.get("user_id")
    testset = TestSet.query.filter(TestSet.id==testset_id).first()
    testset.test_open = 1
    db.session.commit()
    return redirect(url_for('upload._list', userid = userid))

@bp.route('/close/<testset_id>')
def close(testset_id):
    userid = session.get("user_id")
    testset = TestSet.query.filter(TestSet.id==testset_id).first()
    testset.test_open = 0
    db.session.commit()
    return redirect(url_for('upload._list', userid = userid))


# test

@bp.route('/ajax_test/<test_id>', methods=['GET', 'POST'])
def ajax_test(test_id):
    # form = testForm()
    user_id = session.get("user_id")
    if user_id == None:
        return redirect(url_for('auth.login')) 
  
    if request.method == 'POST' and form.validate_on_submit():
        test = request.get_json()
        return print(test)

    return render_template('upload/ajax_test.html', test_id = test_id, user_id = user_id)


@bp.route('/success/<test_id>', methods=['GET', 'POST'])
def success(test_id):
    if request.method == 'POST':
        test_check = Test2.query.filter(Test2.test_id == test_id).all()
        print(test_check)
        for test in test_check:
            db.session.delete(test)
            
        testdata = request.get_json()
        print(testdata)
        for i in testdata:
            test2 = Test2(test_id =test_id, number = testdata.index(i)+1, content = i['text'] )
            print(i['id'], i['text'])
            # 한번 더 중복되는 문항 있는지 확인하고 삭제? -> 중복?? 일단 남겨둠.
            test_check = Test2.query.filter(and_(Test2.test_id==test_id, Test2.number==int(i['id']))).first() 

            if test_check:
                db.session.delete(test_check)
            db.session.add(test2)
            db.session.commit()
        return render_template('upload/success.html', test = testdata)

    return render_template('upload/success.html')


# 이미지 업로드 테스트
from werkzeug.utils import secure_filename
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/upload')
def load_file():
   return render_template('upload/old/image_test.html')

@bp.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        print(type(f))
        if f and allowed_file(f.filename):
            fname = secure_filename(f.filename)
            mtype = f.mimetype

            image_test = ImageTest(name = fname, data = f.read(), mimetype = mtype)
            db.session.add(image_test)
            db.session.commit()
            return 'file uploaded successfully'
        else :
            return '이미지만 올릴 수 있어요'

from flask import Response
@bp.route('/show/<img_id>')
def show(img_id):
    img = ImageTest.query.filter_by(id=img_id).first()
    return Response(img.data, mimetype=img.mimetype)


from flask import send_file
from io import BytesIO
@bp.route('/download')
def download():
    file_data = ImageTest.query.filter_by(id=2).first()
    print(file_data.name)
    return send_file(BytesIO(file_data.data), attachment_filename=file_data.name, as_attachment=True)



# 구버전
@bp.route('/test2', methods=['GET', 'POST'])
def test2():
    form = CreateForm()
    user_id = session.get("user_id")
    if user_id == None:
        return redirect(url_for('auth.login'))
    if request.method == 'POST' and form.validate_on_submit():
        member_id = session['user_id']
        test = TestSet(title=form.title.data, content = form.content.data, create_date=datetime.now(), member_id = member_id)
        db.session.add(test)
        db.session.commit()
        return redirect(url_for('upload._list', userid=user_id))
    return render_template('upload/test2.html', form=form)



