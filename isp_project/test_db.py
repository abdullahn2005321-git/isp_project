import mysql.connector

print("⏳ جارٍ الاتصال بـ 127.0.0.1...")

try:
    
    db_connection = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="",
        database="isp_db",
        port=3306,
        connect_timeout=5,
        use_pure=True,
        ssl_disabled=True
    )
    
    if db_connection.is_connected():
        print("🎉 تم الاتصال بنجاح!")
        db_connection.close()

except mysql.connector.Error as err:
    print(f"❌ خطأ في الاتصال: {err}")
except Exception as err:
    print(f"❌ خطأ غير متوقع: {err}")