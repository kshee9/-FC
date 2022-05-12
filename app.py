import jwt
import hashlib
import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

app = Flask(__name__)

SECRET_KEY = 'SPARTA'

from pymongo import MongoClient
import certifi
ca = certifi.where()
client = MongoClient('mongodb+srv://test:sparta@cluster0.tkoz5.mongodb.net/Cluster0?retryWrites=true&w=majority', tlsCAFile=ca)
db = client.dbsparta

@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


@app.route('/beginner')
def beginner():
    return render_template('beginner.html')


@app.route('/intermediate')
def intermediate():
    return render_template('intermediate.html')


@app.route('/expert')
def expert():
    return render_template('expert.html')


@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find({"username": payload["id"]})
        return render_template('index2.html', user_info=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


# 여기부터 열람 제한
# id에 토큰이 없으면 열람 금지

# def login_info():


@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find({'username': username_receive, 'password': pw_hash})
    print(result)
    if result is not None:
        payload = {
            'id': username_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')

        return jsonify({'result': 'success', 'token': token})
        print("login")
        print(token)
        print(result)
    # 찾지 못하면
    else:
        print("logout")
        print(result)
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "id": username_receive,  # 아이디
        "password": password_hash,  # 비밀번호
        "profile_name": username_receive,  # 프로필 이름 기본값은 아이디
        "profile_pic": "",  # 프로필 사진 파일 이름
        "profile_pic_real": "profile_pics/profile_placeholder.png",  # 프로필 사진 기본 이미지
        "profile_info": ""  # 프로필 한 마디
    }
    db.users.insert_one(doc)
    print(doc)
    return jsonify({'result': 'success'})


@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})




# user token 받아오기
# def get_user_info():
#     token_receive = request.cookies.get('mytoken')
#     # render_params의 자료형은 list로 구성.
#     render_params = {}
#     try:
#         # 유효한 token일 경우 return_params에는 user_info를 삽입해준 뒤 return
#         payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
#         user_info = db.users.find_one({"id": payload["id"]})
#         render_params = user_info
#     except jwt.ExpiredSignatureError:
#         render_params['msg'] = '로그인 시간이 만료되었습니다.'
#     except jwt.exceptions.DecodeError:
#         render_params['msg'] = '로그인 정보가 존재하지 않습니다..'
#     finally:
#         return render_params


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)


