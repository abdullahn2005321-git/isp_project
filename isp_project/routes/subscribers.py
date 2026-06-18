from flask import Blueprint, request, jsonify
from models import db, Area, Subscriber
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from datetime import date
from flask_jwt_extended import jwt_required

subscribers_bp = Blueprint('subscribers', __name__)


#==============================
#=============area endpoints
#==============================
@subscribers_bp.route('/api/areas', methods=['POST'])
@jwt_required()
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
    
@subscribers_bp.route('/api/areas', methods=['GET'])
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

#==============================
#=======subscriber endpoints
#==============================
@subscribers_bp.route('/api/subscribers', methods=['POST'])
@jwt_required()
def add_subscriber():
    data = request.get_json()

    required_fields = ['name', 'phone_number', 'area_id']
    for field in required_fields:
        if field not in data:
            return jsonify({
                "status": "error",
                "message": f"{field} is required."
            }), 400

    new_subscriber = Subscriber(
        name = data['name'],
        phone_number = data['phone_number'],
        area_id = data['area_id'],
        parent_company_id = data.get('parent_company_id', ''),
        balance = float(data.get('balance', 0.0)),
        promise_date = data.get('promise_date') if data.get('promise_date') and data.get('promise_date').strip() != "" else None,
        notes = data.get('notes', '')
    )
    try:
        db.session.add(new_subscriber)
        db.session.commit()
        return jsonify({
            "status" : "success",
            "message": f"Subscriber added successfully'{new_subscriber.name}'.",
            "subscriber_id": new_subscriber.id
        }), 201
    
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": "Phone number already exists."
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@subscribers_bp.route('/api/subscribers', methods=['GET'])
def get_subscribers():
    try:

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)

        pagination = Subscriber.query.options(joinedload(Subscriber.area))\
                                    .filter_by(is_active=True)\
                                    .paginate(page=page, per_page=per_page, error_out=False)

        sub_list = []
        for subscriber in pagination.items:
            sub_list.append({
                "id": subscriber.id,
                "name": subscriber.name,
                "phone_number": subscriber.phone_number,
                "area_id": subscriber.area_id,
                "area_name": subscriber.area.name if subscriber.area else None,
                "parent_company_id": subscriber.parent_company_id,
                "notes": subscriber.notes,
                "balance": subscriber.balance,
                "promise_date": subscriber.promise_date
            })
        
        return jsonify({
            "status": "success",
            "subscribers": sub_list,
            "pagination": {
                "total_subscribers": pagination.total,
                "current_page": pagination.page,
                "total_pages": pagination.pages,
                "has_next": pagination.has_next,
                "has_prev": pagination.has_prev
            }
        }), 200
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@subscribers_bp.route('/api/subscribers/<int:sub_id>', methods=['GET'])
def get_subscriber(sub_id):
    sub = Subscriber.query.get(sub_id)
    if not sub:
        return jsonify({
            "status": "error",
            "message": "Subscriber not found."
        }), 404
    
    sub_data = {
        "id": sub.id,
        "name": sub.name,
        "phone": sub.phone_number if sub.phone_number and sub.phone_number.strip() != "" else "لا يوجد رقم مسجل",
        "area_id": sub.area_id,
        "area_name": sub.area.name if sub.area else None,
        "parent_company_id": sub.parent_company_id,
        "notes": sub.notes,
        "balance": sub.balance,
        "promise_date": str(sub.promise_date) if sub.promise_date else "لا يوجد وعد مسجل"
    }
    return jsonify({
        "status": "success",
        "subscriber": sub_data
    }), 200


@subscribers_bp.route('/api/promises_today', methods=['GET'])
def get_promises_today():
    try:
        today = str(date.today())
        subscribers = Subscriber.query.filter(db.func.date(Subscriber.promise_date) == today).all()

        subs_list = []
        for sub in subscribers:
            subs_list.append({
                "id": sub.id,
                "name": sub.name,
                "phone": sub.phone_number if sub.phone_number and sub.phone_number.strip() != "" else "لا يوجد رقم مسجل",
                "area_id": sub.area_id,
                "area_name": sub.area.name if sub.area else None,
                "parent_company_id": sub.parent_company_id,
                "notes": sub.notes,
                "balance": sub.balance,
                "promise_date": str(sub.promise_date) if sub.promise_date else "لا يوجد وعد مسجل"
            })
        
        return jsonify({
            "status": "success",
            "count": len(subs_list),
            "subscribers": subs_list
        }), 200
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@subscribers_bp.route('/api/subscribers/<int:sub_id>', methods=['PUT'])
@jwt_required()
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

    if 'promise_date' in data:
        sub.promise_date = data['promise_date']

    try:
        db.session.commit()
        return jsonify({
            "status": "success",
            "message": f"Subscriber '{sub.name}' updated successfully."
        }), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": "Phone number already exists."
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@subscribers_bp.route('/api/subscribers/<int:sub_id>', methods=['DELETE'])
@jwt_required()
def delete_subscriber(sub_id):
    sub = Subscriber.query.get(sub_id)
    if not sub:
        return jsonify({
            "status": "error",
            "message": "Subscriber not found."
        }), 404

    try:
        sub.is_active = False
        db.session.commit()
        return jsonify({
            "status": "success",
            "message": f"Subscriber '{sub.name}' deleted successfully."
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
