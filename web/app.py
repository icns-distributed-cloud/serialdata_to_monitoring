from flask import Flask, render_template, jsonify, request, Response
import pymysql
import time
import json

app = Flask(__name__)



@app.route('/')
def home():
    return render_template('home.html')


@app.route('/test', methods=["GET"])
def update():
    def generator():
        while True:
            conn = pymysql.connect(
                host="163.180.117.37",
                port=3306,
                user="testdata",
                passwd="iloveicns",
                db="testdata")

            cursor = conn.cursor()
            query = ("select * from sensor_data order by date desc limit 1")
            cursor.execute(query)
            a = cursor.fetchall()
            b = {"temp": a[0][1]}

            temp = json.dumps(b)
            yield f"data:{temp}\n\n"
            time.sleep(1)
    return Response(generator(), mimetype='text/event-stream')









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
    app.run('163.180.117.111', port=5000, debug=True)
