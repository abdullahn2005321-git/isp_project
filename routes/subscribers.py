from flask import Blueprint, request, jsonify
from models import db, Area, Subscriber, Transaction
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from datetime import date, datetime
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

subscribers_bp = Blueprint('subscribers', __name__)


#==============================
#=============area endpoints
#==============================
@subscribers_bp.route('/api/areas', methods=['POST'])
@jwt_required()
def add_area():
    claims = get_jwt()
    user_role = claims.get("role")
    admin_id = claims.get("admin_id")

    if user_role != "admin":
        return jsonify({"status":"error", "message": "you must be admin"}), 403
    
    data = request.get_json()

    if not data or 'name' not in data or str(data['name']).strip() == "":
        return jsonify({"status": "error", "message": "Area name is required."}), 400

    new_area = Area(
        name=data['name'],
        admin_id=admin_id
    )

    try:
        db.session.add(new_area)
        db.session.commit()
        return jsonify({"status": "success", "message": "Area added successfully."}), 201
    except Exception as e:
        db.session.rollback()
        if "Duplicate entry" in str(e) or "IntegrityError" in str(e):
             return jsonify({"status": "error", "message": "هذه المنطقة موجودة مسبقاً."}), 400
        return jsonify({"status": "error", "message": str(e)}), 500
    
@subscribers_bp.route('/api/areas', methods=['GET'])
@jwt_required()
def get_areas():
    try:
        claims = get_jwt()
        admin_id = claims.get("admin_id")

        areas = Area.query.filter_by(admin_id=admin_id).all()

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

    claims = get_jwt()
    admin_id = claims.get("admin_id")

    data = request.get_json()

    required_fields = ['name', 'phone_number', 'area_id']
    for field in required_fields:
        if field not in data:
            return jsonify({
                "status": "error",
                "message": f"{field} is required."
            }), 400

    area = Area.query.filter_by(id=data['area_id'], admin_id=admin_id).first()
    if not area:
        return jsonify({
            "status": "error",
            "message": "Area not found or unauthorized."
        }), 403
    
    new_subscriber = Subscriber(
        name = data['name'],
        phone_number = data['phone_number'],
        area_id = data['area_id'],
        balance = float(data.get('balance', 0.0)),
        promise_date = data.get('promise_date', None),
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
@jwt_required()
def get_subscribers():
    try:
        claims = get_jwt()
        admin_id = claims.get("admin_id")

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        search = request.args.get('search', '', type=str)
        debt_only = str(request.args.get('debt_only', 'false')).strip().lower() in ('1', 'true', 'yes', 'on')
        renewal_from_raw = request.args.get('renewal_from', '', type=str).strip()
        renewal_to_raw = request.args.get('renewal_to', '', type=str).strip()

        renewal_from = None
        renewal_to = None

        if renewal_from_raw:
            try:
                renewal_from = datetime.strptime(renewal_from_raw, "%Y-%m-%d").date()
            except ValueError:
                return jsonify({
                    "status": "error",
                    "message": "صيغة تاريخ البداية غير صحيحة. استخدم YYYY-MM-DD."
                }), 400

        if renewal_to_raw:
            try:
                renewal_to = datetime.strptime(renewal_to_raw, "%Y-%m-%d").date()
            except ValueError:
                return jsonify({
                    "status": "error",
                    "message": "صيغة تاريخ النهاية غير صحيحة. استخدم YYYY-MM-DD."
                }), 400

        if renewal_from and renewal_to and renewal_from > renewal_to:
            return jsonify({
                "status": "error",
                "message": "تاريخ البداية يجب أن يكون أقدم أو يساوي تاريخ النهاية."
            }), 400

        last_renewal_subquery = db.session.query(
            Transaction.subscriber_id.label('subscriber_id'),
            db.func.max(Transaction.transaction_date).label('last_renewal_date')
        ).filter(
            Transaction.transaction_type == 'renewal'
        ).group_by(
            Transaction.subscriber_id
        ).subquery()

        query = db.session.query(
            Subscriber,
            last_renewal_subquery.c.last_renewal_date.label('last_renewal_date')
        ).join(
            Area,
            Subscriber.area_id == Area.id
        ).outerjoin(
            last_renewal_subquery,
            last_renewal_subquery.c.subscriber_id == Subscriber.id
        ).options(
            joinedload(Subscriber.area)
        ).filter(
            Area.admin_id == admin_id,
            Subscriber.is_active == True
        )

        if search and search.strip():
            search_term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Subscriber.name.ilike(search_term),
                    Subscriber.phone_number.ilike(search_term)
                )
            )

        if debt_only:
            query = query.filter(Subscriber.balance < 0)

        if renewal_from:
            query = query.filter(db.func.date(last_renewal_subquery.c.last_renewal_date) >= renewal_from)

        if renewal_to:
            query = query.filter(db.func.date(last_renewal_subquery.c.last_renewal_date) <= renewal_to)

        if renewal_from or renewal_to:
            query = query.order_by(last_renewal_subquery.c.last_renewal_date.asc(), Subscriber.id.asc())
        else:
            query = query.order_by(Subscriber.id.desc())

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        sub_list = []
        for subscriber, last_renewal_date in pagination.items:
            sub_list.append({
                "id": subscriber.id,
                "name": subscriber.name,
                "phone_number": subscriber.phone_number,
                "area_id": subscriber.area_id,
                "area_name": subscriber.area.name if subscriber.area else None,
                "notes": subscriber.notes,
                "balance": subscriber.balance,
                "promise_date": subscriber.promise_date.strftime("%Y-%m-%d") if subscriber.promise_date else "لا يوجد وعد مسجل",
                "last_renewal_date": last_renewal_date.strftime("%Y-%m-%d") if last_renewal_date else None
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
@jwt_required()
def get_subscriber(sub_id):
    claims = get_jwt()
    admin_id = claims.get("admin_id")

    sub = Subscriber.query.join(Area).filter(
            Subscriber.id == sub_id,
            Area.admin_id == admin_id,
            Subscriber.is_active == True
        ).first()
    
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
        "notes": sub.notes,
        "balance": sub.balance,
        "promise_date": sub.promise_date.strftime("%Y-%m-%d") if sub.promise_date else "لا يوجد وعد مسجل"
    }
    return jsonify({
        "status": "success",
        "subscriber": sub_data
    }), 200


@subscribers_bp.route('/api/promises_today', methods=['GET'])
@jwt_required()
def get_promises_today():
    try:
        claims = get_jwt()
        admin_id = claims.get("admin_id")

        today = str(date.today())
        subscribers = Subscriber.query.join(Area).filter(
            db.func.date(Subscriber.promise_date) == today,
            Subscriber.is_active == True,
            Area.admin_id == admin_id
        ).options(joinedload(Subscriber.area)).all()

        subs_list = []
        for sub in subscribers:
            subs_list.append({
                "id": sub.id,
                "name": sub.name,
                "phone": sub.phone_number if sub.phone_number and sub.phone_number.strip() != "" else "لا يوجد رقم مسجل",
                "area_id": sub.area_id,
                "area_name": sub.area.name if sub.area else None,
                "notes": sub.notes,
                "balance": sub.balance,
                "promise_date": sub.promise_date.strftime("%Y-%m-%d") if sub.promise_date else "لا يوجد وعد مسجل"
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
    claims = get_jwt()
    admin_id = claims.get("admin_id")

    sub = Subscriber.query.join(Area).filter(
        Subscriber.id == sub_id,
        Area.admin_id == admin_id
    ).first()

    if not sub:
        return jsonify({
            "status": "error",
            "message": "Subscriber not found."
        }), 404

    data = request.get_json()

    if 'area_id' in data:

        new_area = Area.query.filter_by(id=data['area_id'], admin_id=admin_id).first()
        if not new_area:
            return jsonify({
                "status": "error",
                "message": "Area not found or access denied."
            }), 404
        sub.area_id = data['area_id']
    
    if 'phone_number' in data:
        sub.phone_number = data['phone_number']
    
    if 'name' in data:
        sub.name = data['name']
     
    if 'notes' in data:
        sub.notes = data['notes']

    if 'promise_date' in data:
        raw_data = data['promise_date']
        sub.promise_date = raw_data if raw_data and str(raw_data).strip() != "" else None

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
    claims = get_jwt()
    admin_id = claims.get("admin_id")
    admin_role = claims.get("role")

    if admin_role != "admin":
        return jsonify({
            "status": "error",
            "message": "you must be admin"
        }), 403
    
    sub = Subscriber.query.join(Area).filter(Subscriber.id == sub_id, Area.admin_id == admin_id).first()

    if not sub:
        return jsonify({
            "status": "error",
            "message": "Subscriber not found or you don't have permission to modify it."
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
