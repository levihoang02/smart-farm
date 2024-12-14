import mysql.connector

def getAllThreshold():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="312002VH",
        database="iot_data",
        port=3310
    )
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM threshold")
        thresholds = cursor.fetchall()
        return thresholds
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
            
def updateThresholdBySensor(sensor, newValue):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="312002VH",
        database="iot_data",
        port=3310,
    )
    try:
        cursor = conn.cursor()
        sql = "UPDATE threshold SET value = %s WHERE sensor = %s"
        cursor.execute(sql, (newValue, sensor))
        conn.commit()
        return cursor.rowcount > 0
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
    