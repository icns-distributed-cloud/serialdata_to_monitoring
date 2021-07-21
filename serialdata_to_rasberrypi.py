import pymysql
import minimalmodbus
import os, sys, time
import datetime

instrument1 = minimalmodbus.Instrument('/dev/ttyUSB0', 1)  # temperature & humidity (USBport, slave ID)
instrument1.serial.baudrate = 9600
instrument1.serial.parity = 'N'
instrument1.serial.stopbits = 1
instrument1.serial.timeout = 5
instrument1.serial.bytesize = 8

instrument2 = minimalmodbus.Instrument('/dev/ttyUSB0', 80)  # gyro (USBport, slave ID)
instrument2.serial.baudrate = 9600
instrument2.serial.parity = 'N'
instrument2.serial.stopbits = 1
instrument2.serial.timeout = 5
instrument2.serial.bytesize = 8

minimalmodbus.CLOSE_PORT_AFTER_EACH_CALL = True


# def main():
#    print("Restart")
#    executable = sys.executable
#    args = sys.argv[:]
#    args.insert(0, sys.executable)

#   time.sleep(1)
#   print("Respawning")

def restart():
    os.execl(sys.executable, sys.executable, *sys.argv)
    print("Restart")
    time.sleep(1)


conn = pymysql.connect(  # db imformation
    host="163.180.117.37",
    port=3306,
    user="testdata",
    passwd="iloveicns",
    db="testdata")

now = time.localtime()

try:
    with conn.cursor() as cur:
        sql = "insert into sensor_data(date, temperature, humidity, gyro_x, gyro_y) values(%s, %s, %s, %s, %s)"

        while True:
            sensor_temp = instrument1.read_register(0,1)   # (sensor address, float)
            sensor_humid = instrument1.read_register(1,1)
            sensor_gyro_x = instrument2.read_register(61,5)
            sensor_gyro_y = instrument2.read_register(62,5)

            print("%04d/%02d/%02d %02d:%02d:%02d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec))
            print("temperature: ", sensor_temp, "humidity: ", sensor_humid)
            print("gyro_x: ", sensor_gyro_x, "gryo_y: ", sensor_gyro_y)




            if sensor_temp is not None and sensor_humid is not None and sensor_gyro_x is not None and sensor_gyro_y is not None:   # insert data

                cur.execute(sql,(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), sensor_temp, sensor_humid, sensor_gyro_x, sensor_gyro_y))
                conn.commit()
            else:

                print("Failed to get reading.")
            time.sleep(1)

#except minimalmodbus.NoResponseError:

except :
    restart()

finally :
    conn.close()


if __name__ == "__main__":
   restart()

