from flask import Flask , request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.json.ensure_ascii = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@127.0.0.1/isp_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



db = SQLAlchemy(app)

@app.route('/')
def home():
    return {
        "status": "success",
        "message": "🚀 مرحباً بك في نظام إدارة المشتركين! السيرفر يعمل وجاهز لاستقبال البيانات."
    }

if __name__ == '__main__':
    app.run(debug=True)