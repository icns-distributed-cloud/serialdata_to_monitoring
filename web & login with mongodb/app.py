from flask import Flask, render_template, jsonify, request, Response
import pymysql
import time
import json
from pymongo import MongoClient


import jwt
import datetime
import hashlib


app = Flask(__name__)

client = MongoClient('localhost', 27017)

db = client.project

SECRET_KEY = 'sparta'

app.config['SECRET_KEY'] = 'BCODE_Flask'



@app.route('/', methods=["GET", "POST"])
def main():
    return render_template('Next.html')

@app.route('/Login')
def Login():
    return render_template('Login.html')

@app.route('/api/signup', methods=['POST'])
def make_sign():
    id_receive = request.form['ID_give']
    password_receive = request.form['Password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()

    info = {
        'ID': id_receive,
        'Password': pw_hash,
    }
    overlap = db.infos.count_documents({'ID': id_receive})

    if overlap == 0:
        db.infos.insert_one(info)
        return jsonify({'result': 'success', 'msg': '회원가입이 완료되었습니다'})
    else:
        return jsonify({'result': 'fail', 'msg': '중복된 아이디입니다.'})



# 로그인 API

@app.route('/api/Login', methods=['POST'])
def api_login():
    id_receive = request.form['ID_give']
    password_receive = request.form['Password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()

    # id, 암호화된 pw을 가지고 해당 유저를 찾습니다.
    check = db.infos.find_one({'ID': id_receive, 'Password': pw_hash})

    # 찾으면 JWT 토큰을 만들어 발급합니다.
    if check is not None:
        # JWT 토큰에는, payload와 시크릿키가 필요
        # 시크릿키가 있어야 토큰을 디코딩(=풀기) 해서 payload 값을 볼 수 있음
        # id와 exp를 담고 JWT 토큰을 풀면 유저ID 값을 알 수 있습니다.
        # exp에는 만료시간. 만료시간이 지나면, 시크릿키로 토큰을 풀 때 만료되었다고 에러가 남
        payload = {
            'ID': id_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=600)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        # token을 줍니다.
        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


# [유저 정보 확인 API]
# 로그인된 유저만 call 할 수 있는 API.
@app.route('/api/Next', methods=['GET'])
def api_valid():
    # header에 저장해서 넘겨주어 토큰을 주고 받음
    token_receive = request.headers['token_give']

    try:
        # token을 시크릿키로 디코딩
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        print(payload)
        # payload 안에 id로 유저정보 찾음
        # 닉네임을 보내줌
        userinfo = db.infos.find_one({'ID': payload['ID']}, {'_id': 0})
        return jsonify({'result': 'success', 'ID': userinfo['ID']})

    except jwt.ExpiredSignatureError:
        # 만료시간이 지났으면 에러발생
        return jsonify({'result': 'fail', 'msg': '로그인을 해주세요.'})






# @app.route('/test', methods=["GET"])
# def update():
#     def generator():
#         while True:
#             conn = pymysql.connect(
#                 host="163.180.117.37",
#                 port=3306,
#                 user="testdata",
#                 passwd="iloveicns",
#                 db="testdata")
#
#             cursor = conn.cursor()
#             query = ("select * from sensor_data order by date desc limit 1")
#             cursor.execute(query)
#             a = cursor.fetchall()
#             b = {"temp": a[0][1]}
#
#             temp = json.dumps(b)
#             yield f"data:{temp}\n\n"
#             time.sleep(1)
#     return Response(generator(), mimetype='text/event-stream')









@app.route('/five', methods=["GET", "POST"])
def five():
    return render_template('five.html')

@app.route('/5-monitoring', methods=["GET", "POST"])
def monitoring():
    return render_template('5-monitoring.html')

@app.route('/5-CCTV', methods=["GET", "POST"])
def CCTV():
    return render_template('5-CCTV.html')



if __name__ == '__main__':
    app.run('localhost', port=5000, debug=True)
