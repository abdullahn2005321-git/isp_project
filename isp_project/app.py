from flask import Flask , request, jsonify
from models import db, Area, Subscriber, Payment

app = Flask(__name__)
app.json.ensure_ascii = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@127.0.0.1/isp_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# area endpoints
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


# subscriber endpoints
@app.route('/api/subscribers', methods=['POST'])
def add_subscriber():
    data = request.get_json()

    required_fields = ['name', 'phone_number', 'area_id']
    for field in required_fields:
        if field not in data:
            return jsonify({"status": "error", "message": f"{field} is required."}), 400

    new_subscriber = Subscriber(
        name = data['name'],
        phone_number = data['phone_number'],
        area_id = data['area_id'],
        parent_company_id = data.get('parent_company_id', ''),
        notes = data.get('notes', '')
    )
    try:
        db.session.add(new_subscriber)
        db.session.commit()
        return jsonify({
            "status" : "success",
            "message": f"Subscriber added successfully'{new_subscriber.name}'."
        }), 201
    except Exception as e:
        db.session.rollback()
        if 'phone_number' in str(e).lower() or 'duplicate' in str(e).lower():
            return jsonify({
                "status": "error",
                "message": "Phone number already exists."
            }), 400
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/subscribers', methods=['GET'])
def get_subscribers():
    try:
        subscribers = Subscriber.query.all()

        sub_list = []
        for subscriber in subscribers:
            sub_list.append({
                "id": subscriber.id,
                "name": subscriber.name,
                "phone_number": subscriber.phone_number,
                "area_id": subscriber.area_id,
                "parent_company_id": subscriber.parent_company_id,
                "notes": subscriber.notes
            })
        
        return jsonify({
            "status": "success",
            "total": len(sub_list),
            "subscribers": sub_list
        }), 200
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/subscribers/<int:sub_id>', methods=['PUT'])
def update_subscriber(sub_id):

    sub = Subscriber.query.get(sub_id)
    if not sub:
        return jsonify({
            "status": "error",
            "message": "Subscriber not found."
        }), 404

    data = request.get_json()

    if 'area_id' in data:

        new_area = Area.query.get(data['area_id'])
        if not new_area:
            return jsonify({
                "status": "error",
                "message": "Area not found."
            }), 404
        sub.area_id = data['area_id']
    
    if 'phone_number' in data:
        sub.phone_number = data['phone_number']
    
    if 'name' in data:
        sub.name = data['name']
    
    if 'parent_company_id' in data:
        sub.parent_company_id = data['parent_company_id']
    
    if 'notes' in data:
        sub.notes = data['notes']

    try:
        db.session.commit()
        return jsonify({
            "status": "success",
            "message": f"Subscriber '{sub.name}' updated successfully."
        }), 200
    except Exception as e:
        db.session.rollback()

        if 'phone_number' in str(e).lower() or 'duplicate' in str(e).lower():
            return jsonify({
                "status": "error",
                "message": "Phone number already exists."
            }), 400

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    

if __name__ == '__main__':
    app.run(debug=True)