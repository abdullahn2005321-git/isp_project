from flask import Flask , request, jsonify
from models import db, Area, Subscriber, Payment
app = Flask(__name__)
app.json.ensure_ascii = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@127.0.0.1/isp_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


@app.route('/api/areas', methods=['POST'])
def add_area():
    data = request.get_json()

    if not data or 'name' not in data:
        return jsonify({"status": "error", "message": "Area name is required."}), 400
    
    new_area = Area(name=data['name'])

    try:
        db.session.add(new_area)
        db.session.commit()
        return jsonify({"status": "success", "message": "Area added successfully."}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    
@app.route('/api/areas', methods=['GET'])
def get_areas():
    try:
        areas = Area.query.all()
        
        areas_list = [{"id": area.id, "name": area.name} for area in areas]
        return jsonify({
            "status": "success",
            "areas": areas_list
        }), 200
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)