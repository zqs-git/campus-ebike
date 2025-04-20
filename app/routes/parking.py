# 查看停车场信息
from datetime import datetime
from flask import Blueprint, jsonify, request
from app import db
from app.models.parking import ParkingLot, ParkingSpace, ParkingRecord
from sqlalchemy.orm import joinedload

parking_bp = Blueprint('parking', __name__,url_prefix='/api/parking')

@parking_bp.route('/parking_lots', methods=['GET'])
def get_parking_lots():
    parking_lots = ParkingLot.query.all()
    return jsonify([{
        'id': lot.id,
        'name': lot.name,
        'location': lot.location.name,
        'capacity': lot.capacity,
        'occupied': lot.occupied
    } for lot in parking_lots])

# 获取停车场详细信息
@parking_bp.route('/parking_lot/<int:lot_id>', methods=['GET'])
def get_parking_lot_detail(lot_id):
    parking_lot = ParkingLot.query.get(lot_id)
    if not parking_lot:
        return jsonify({"message": "停车场不存在"}), 404
    
    # 获取停车位列表
    parking_spaces = ParkingSpace.query.filter_by(parking_lot_id=lot_id).all()
    spaces_info = [{
        'id': space.id,
        'status': space.status
    } for space in parking_spaces]
    
    # 返回停车场详细信息
    return jsonify({
        "id": parking_lot.id,
        "name": parking_lot.name,
        "location": parking_lot.location.name,
        "capacity": parking_lot.capacity,
        "occupied": parking_lot.occupied,
        "available": parking_lot.capacity - parking_lot.occupied,
        "spaces": spaces_info
    }), 200



# 创建停车场
@parking_bp.route('/add_parking_lot', methods=['POST'])
def add_parking_lot():
    data = request.get_json()
    location_id = data['location_id']
    name = data['name']
    capacity = data['capacity']

    parking_lot = ParkingLot(location_id=location_id, name=name, capacity=capacity)
    db.session.add(parking_lot)
    db.session.commit()
    
    # 创建停车位
    for _ in range(capacity):
        parking_space = ParkingSpace(parking_lot_id=parking_lot.id)
        db.session.add(parking_space)
    
    db.session.commit()

    return jsonify({"message": "停车场创建成功"}), 201

@parking_bp.route('/park_in', methods=['POST'])
def park_in():
    data = request.get_json()
    print("收到的数据:", data)  

    lot_id = data['lot_id']
    vehicle_id = data['vehicle_id']
    user_id = data['user_id']

    # 查找停车场
    parking_lot = ParkingLot.query.get(lot_id)
    if not parking_lot:
        return jsonify({"message": "停车场不存在"}), 404

    # 查找空闲停车位
    available_space = ParkingSpace.query.filter_by(parking_lot_id=lot_id, status='available').first()
    if not available_space:
        return jsonify({"message": "停车场已满"}), 400

    # 更新停车位状态为“占用”
    available_space.status = 'occupied'

    # ✅ 更新停车场 occupied +1
    parking_lot.occupied += 1  

    # 创建停车记录
    parking_record = ParkingRecord(user_id=user_id, vehicle_id=vehicle_id, parking_space_id=available_space.id)
    db.session.add(parking_record)

    # 提交所有更改
    db.session.commit()

    return jsonify({"message": "停车成功"}), 200




# 停车出库
@parking_bp.route('/park_out/<int:record_id>', methods=['POST'])
def park_out(record_id):
    record = ParkingRecord.query.get(record_id)
    if not record:
        return jsonify({"message": "停车记录不存在"}), 404

    # 找到停车位
    parking_space = ParkingSpace.query.get(record.parking_space_id)
    parking_lot = ParkingLot.query.get(parking_space.parking_lot_id)

    # 更新停车位状态为“空闲”
    parking_space.status = 'available'

    # ✅ 更新停车场 occupied -1
    if parking_lot.occupied > 0:
        parking_lot.occupied -= 1  

    # 更新停车记录，添加出库时间
    record.park_out_time = datetime.utcnow()

    # 提交所有更改
    db.session.commit()

    return jsonify({"message": "取车成功"}), 200



# 获取停车记录
@parking_bp.route('/current_record', methods=['GET'])
def get_current_record():
    # 从请求头获取用户ID（需配合前端发送）
    user_id = request.headers.get('X-User-ID')
    
    if not user_id:
        return jsonify({"message": "未提供用户信息"}), 401

    # 添加关系加载优化查询（第2处修改）
    current_record = ParkingRecord.query.options(
        db.joinedload(ParkingRecord.parking_space),
        db.joinedload(ParkingRecord.vehicle)
    ).filter_by(
        user_id=user_id,
        park_out_time=None
    ).first()

    # 添加空值保护（第3处修改）
    if not current_record or not current_record.parking_space:
        return jsonify({"message": "未找到有效停车记录"}), 404

    # 返回结构化数据
    return jsonify({
        "id": current_record.id,
        "lot_id": current_record.parking_space.parking_lot_id,
        "entry_time": current_record.park_in_time.isoformat(),
        "plate_number": current_record.vehicle.plate_number
    }), 200


# 更新停车场信息
@parking_bp.route('/parking_lot/<int:lot_id>', methods=['PUT'])
def update_parking_lot(lot_id):
    data = request.get_json()
    parking_lot = ParkingLot.query.get(lot_id)

    if not parking_lot:
        return jsonify({"message": "停车场不存在"}), 404

    parking_lot.name = data.get('name', parking_lot.name)
    parking_lot.capacity = data.get('capacity', parking_lot.capacity)

    db.session.commit()
    return jsonify({"message": "停车场信息更新成功"}), 200


# 删除停车场
@parking_bp.route('/parking_lot/<int:lot_id>', methods=['DELETE'])
def delete_parking_lot(lot_id):
    parking_lot = ParkingLot.query.get(lot_id)

    if not parking_lot:
        return jsonify({"message": "停车场不存在"}), 404

    # 删除所有相关停车位和停车记录
    ParkingSpace.query.filter_by(parking_lot_id=lot_id).delete()
    ParkingRecord.query.filter(
        ParkingRecord.parking_space_id.in_(
            db.session.query(ParkingSpace.id).filter_by(parking_lot_id=lot_id)
        )
    ).delete()

    db.session.delete(parking_lot)
    db.session.commit()
    
    return jsonify({"message": "停车场删除成功"}), 200



# 获取所有停车记录
@parking_bp.route('/parking_records', methods=['GET'])
def get_parking_records():
    keyword = request.args.get('keyword', '').strip()  # 车牌号搜索
    page = int(request.args.get('page', 1))  # 当前页码
    page_size = int(request.args.get('pageSize', 10))  # 每页数量

    # 预加载关联数据，优化查询效率
    query = ParkingRecord.query.options(
        joinedload(ParkingRecord.vehicle),
        joinedload(ParkingRecord.parking_space)
    )

    # 如果提供了 keyword，则进行搜索
    if keyword:
        query = query.filter(ParkingRecord.vehicle.plate_number.contains(keyword))

    # 获取总条数（分页前）
    total_records = query.count()

    # 执行分页查询
    records = query.order_by(ParkingRecord.park_in_time.desc()) \
                   .offset((page - 1) * page_size) \
                   .limit(page_size) \
                   .all()

    # 结构化返回数据
    return jsonify({
        "records": [{
            "id": record.id,
            "user_id": record.user_id,
            "vehicle_id": record.vehicle.id,
            "plate_number": record.vehicle.plate_number,
            "lot_id": record.parking_space.parking_lot_id,
            "entry_time": record.park_in_time.isoformat(),
            "exit_time": record.park_out_time.isoformat() if record.park_out_time else None
        } for record in records],
        "total": total_records
    }), 200

