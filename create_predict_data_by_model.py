from influxdb import InfluxDBClient
import json
import time
import datetime
import pandas as pd
import numpy as np
import tensorflow as tf
import pymysql
import threading
from numpy import argmax
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.models import load_model
from tensorflow.keras.layers import LSTM
from tensorflow.keras.layers import Dense, SimpleRNN, Activation
from tensorflow.keras import optimizers
import sys
import os


def load_pre_model():
    model = Sequential()
    model.add(LSTM(50, input_shape=(3, 2), return_sequences=True))
    model.add(LSTM(50, input_shape=(3, 2)))
    model.add(Dense(50, activation='relu'))
    model.add(Dense(25, activation='relu'))
    model.add(Dense(2))
    model.compile(loss='mse', optimizer='Adam', metrics=['accuracy'])

    model = load_model('save_model_2.h5')

    return model


def get_influx(db, host='163.180.117.37', port=8086, user='icns', passwd='iloveicns'):
    # connect to the InfluxDB
    client = InfluxDBClient(host, port, user, passwd, db)
    try:
        client.switch_database(db)
        print('=====================')
        print('Connection Successful')
        print('=====================')
        print(' InfluxDB  Connected ')
        print('=====================')
        print('                     ')
    except:
        # Generate error if you can't connect database
        print('=====================')
        print('  Connection Failed  ')
        print('=====================')

        pass

    return client


def get_mysql():
    # connect to the MySQL DB
    data_db = pymysql.connect(
        host='163.180.117.37',
        port=3306,
        user='testdata',
        passwd='iloveicns',
        db='testdata'
    )
    # Make cursor
    cursor = data_db.cursor(pymysql.cursors.DictCursor)

    return cursor


def input_json(json_body, measurement, temp, hum, time):
    # Update json
    json_body[0]["measurement"] = measurement
    json_body[0]["fields"]["Temperature"] = temp
    json_body[0]["fields"]["Humidity"] = hum
    json_body[0]["date"] = time

    return json_body


def startPredict(client, sc, model, json_body):
    # DB connection
    cursor = get_mysql()

    # Input from MySQL
    cursor.execute("SELECT * FROM sensor_data ORDER BY date DESC LIMIT 3")
    recent_34 = np.flip(np.array(cursor.fetchall()))
    input_data = []
    msm_curr = 'current'

    # Store input in influxdb
    for i in range(3):
        temp = recent_34[i]['temperature']
        hum = recent_34[i]['humidity']
        time = recent_34[i]['date']
        #print(time)
        input_data.append([temp, hum])
        json_34 = input_json(json_body, msm_curr, float(temp), float(hum), time)
        client.write_points(json_34)

    current_time = datetime.datetime.utcnow()
    #print(current_time)
    future_time = current_time + datetime.timedelta(seconds=30) + datetime.timedelta(hours=9)
    print(future_time)

    # Preprocessing
    input_data = np.array(input_data)
    normalized_input_data = sc.fit_transform(np.float64(input_data))
    Reshaped_normalized_input_data = normalized_input_data.reshape(1, 3, 2)
    # print('Shape of normalized_input_data: ', Reshaped_normalized_input_data.shape)

    # Prediction
    result = model.predict(Reshaped_normalized_input_data)
    # print('Normalized predict result: ',result)
    result_inv = sc.inverse_transform(result)
    #print('Prediction result ', result_inv, 'has been stored in influxdb')

    # Store output in influxdb
    result_temp = result_inv[0][0]
    result_hum = result_inv[0][1]
    msm_fut = 'future'
    input_json(json_body, msm_fut, result_temp, result_hum, future_time)
    client.write_points(json_body)

    print(result_inv[0])


    conn = pymysql.connect(  # db imformation
        host="163.180.117.37",
        port=3306,
        user="testdata",
        passwd="iloveicns",
        db="testdata")

    with conn.cursor() as cur:
        sql = "insert into pred_data(future, pred_temp, pred_hum) values(%s, %s, %s)"

        # while True:

        if result_temp is not None and result_hum is not None:  # insert data

            cur.execute(sql, (
                time.strftime(str(future_time)), result_temp, result_hum
               ))
            conn.commit()
        else:
             print("Failed to get reading.")


    # Recurrence
    timer = threading.Timer(1, startPredict, [client, sc, model, json_body])
    timer.start()





if __name__ == '__main__':
    # Initiate json for input
    json_body = [
        {
            "measurement": "current",
            "tags": {
                "user": "icns"
            },
            "date": "2021-01-01T8:01:00Z",
            "fields": {
                "Temperature": 0,
                "Humidity": 0
            }
        }
    ]
    # Load model
    model = load_pre_model()

    # Generate scaler
    sc = MinMaxScaler()

    # Connect MySQL
    cursor = get_mysql()

    # Connect influxdb
    client = get_influx('data')

    startPredict(client, sc, model, json_body)