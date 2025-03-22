from flask import Blueprint, request, jsonify
from app import db
from app.models.users import User
from app.models.vehicles import ElectricVehicle
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.permissions import role_required  # ✅ 从权限模块导入
from flask_cors import cross_origin  # ✅ 导入跨域扩展
vehicle_bp = Blueprint('vehicle', __name__, url_prefix='/api/vehicle')

@vehicle_bp.route('/bind', methods=['POST'])
@jwt_required()
def bind_vehicle():
    """
    电动车绑定接口
    绑定当前用户和电动车（通过车牌号）
    请求体示例:
    {
        "plate_number": "京A12345",
        "brand": "Yadea",
        "model": "G5",
        "color": "Black",
        "battery_capacity": 1200,
        "status": "active"
    }
    """
    print("Entering bind_vehicle route")  # 打印调试信息
    data = request.get_json()

    # 确保请求数据中包含必要字段
    if not data or 'plate_number' not in data or 'brand' not in data or 'model' not in data:
        return jsonify({"code": 400, "msg": "请求数据不完整"}), 400

    plate_number = data['plate_number']
    brand = data['brand']
    model = data['model']
    color = data.get('color', None)  # 颜色是可选的
    battery_capacity = data.get('battery_capacity', None)  # 电池容量是可选的
    status = data.get('status', 'active')  # 默认状态为 'active'

    # 获取当前用户
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"code": 404, "msg": "用户不存在"}), 404

    # 检查该用户是否已经绑定了电动车
    if ElectricVehicle.query.filter_by(owner_id=user_id).first():
        return jsonify({"code": 400, "msg": "该用户已绑定电动车"}), 400

    # 检查车牌号是否已经被绑定
    existing_vehicle = ElectricVehicle.query.filter_by(plate_number=plate_number).first()
    if existing_vehicle:
        return jsonify({"code": 400, "msg": "该车牌已被绑定"}), 400

    # 创建电动车并绑定
    new_vehicle = ElectricVehicle(
        plate_number=plate_number,
        brand=brand,
        model=model,
        color=color,
        battery_capacity=battery_capacity,
        status=status,
        owner_id=user_id
    )

    try:
        db.session.add(new_vehicle)
        db.session.commit()
        return jsonify({
            "code": 201,
            "msg": "电动车绑定成功",
            "vehicle": {  # 将字段嵌套在 vehicle 对象中
                "vehicle_id": new_vehicle.id,
                "plate_number": new_vehicle.plate_number,
                "brand": new_vehicle.brand,
                "model": new_vehicle.model,
                "color": new_vehicle.color,
                "battery_capacity": new_vehicle.battery_capacity,
                "status": new_vehicle.status
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "code": 500, 
            "msg": "电动车绑定失败", 
            "details": str(e)
        }), 500


@vehicle_bp.route('/my_vehicle', methods=['GET'])
@jwt_required()
def get_bound_vehicle():
    """
    获取当前用户绑定的电动车信息
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"code": 404, "msg": "用户不存在"}), 404

    # 查询用户绑定的电动车
    vehicle = ElectricVehicle.query.filter_by(owner_id=user_id).first()

    if not vehicle:
        return jsonify({"code": 404, "msg": "未绑定电动车"}), 404

    return jsonify({
        "code": 200,
        "msg": "电动车信息",
        "vehicle": {
            "vehicle_id": vehicle.id,
            "plate_number": vehicle.plate_number,
            "brand": vehicle.brand,
            "model": vehicle.model,
            "color": vehicle.color,
            "battery_capacity": vehicle.battery_capacity,
            "status": vehicle.status
        }
    }), 200


@vehicle_bp.route('/admin_vehicle', methods=['GET'])
@jwt_required()
# @role_required('admin')  # ✅ 只允许管理员访问
# @cross_origin(origin="http://localhost:8080", supports_credentials=True)  # ✅ 单独配置
def get_all_vehicles():
    """获取所有车辆信息（管理员专属接口）"""
    vehicles = ElectricVehicle.query.all()

    return jsonify({
        "code": 200,
        "data": [vehicle.serialize() for vehicle in vehicles]
    }), 200


@vehicle_bp.route('/unbind', methods=['POST'])
@jwt_required()
def unbind_vehicle():
    """
    电动车解绑接口
    """
    data = request.get_json()

    if not data or 'vehicle_id' not in data:
        return jsonify({"code": 400, "msg": "请求数据不完整"}), 400

    vehicle_id = data['vehicle_id']

    # 获取当前用户
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"code": 404, "msg": "用户不存在"}), 404

    # 查询该用户的电动车
    vehicle = ElectricVehicle.query.filter_by(owner_id=user_id, id=vehicle_id).first()

    if not vehicle:
        return jsonify({"code": 404, "msg": "电动车不存在或不属于当前用户"}), 404

    try:
        db.session.delete(vehicle)
        db.session.commit()
        return jsonify({"code": 200, "msg": "电动车解绑成功"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "msg": "电动车解绑失败", "details": str(e)}), 500


@vehicle_bp.route('/update', methods=['PUT'])  # 改为 PUT 请求
@jwt_required()
def update_vehicle():
    """
    更新电动车信息接口
    """
    data = request.get_json()

    if not data or 'vehicle_id' not in data:
        return jsonify({"code": 400, "msg": "请求数据不完整"}), 400

    vehicle_id = data['vehicle_id']
    new_brand = data.get('brand')
    new_color = data.get('color')
    new_model = data.get('model')
    new_plate_number = data.get('plate_number')
    new_battery_capacity = data.get('battery_capacity') 

    # 获取当前用户
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"code": 404, "msg": "用户不存在"}), 404

    # 查询电动车
    vehicle = ElectricVehicle.query.filter_by(owner_id=user_id, id=vehicle_id).first()

    if not vehicle:
        return jsonify({"code": 404, "msg": "电动车不存在或不属于当前用户"}), 404

    # 更新电动车信息
    if new_plate_number:
        existing_vehicle = ElectricVehicle.query.filter_by(plate_number=new_plate_number).first()
        if existing_vehicle:
            return jsonify({"code": 400, "msg": "该车牌已被绑定"}), 400
        vehicle.plate_number = new_plate_number
    if new_brand:
        vehicle.brand = new_brand
    if new_color:
        vehicle.color = new_color
    if new_model:
        vehicle.model = new_model
    if new_battery_capacity:
        vehicle.battery_capacity = new_battery_capacity

    try:
        db.session.commit()
        return jsonify({
            "code": 200,
            "msg": "电动车信息更新成功",
            "vehicle": {
                "vehicle_id": vehicle.id,
                "plate_number": vehicle.plate_number,
                "brand": vehicle.brand,
                "model": vehicle.model,
                "color": vehicle.color,
                "battery_capacity": vehicle.battery_capacity,
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "msg": "电动车信息更新失败", "details": str(e)}), 500


@vehicle_bp.route('/admin_update_vehicles/<int:vehicle_id>', methods=['PUT'])
# @role_required('admin')
@jwt_required()
def admin_update_vehicles(vehicle_id):
    data = request.json
    vehicle = ElectricVehicle.query.get(vehicle_id)
    if not vehicle:
        return jsonify({"code": 404, "msg": "车辆不存在"}), 404
    # 更新字段
    vehicle.plate_number = data.get('plate_number', vehicle.plate_number)
    vehicle.status = data.get('status', vehicle.status)
    # 其他字段...
    db.session.commit()
    return jsonify({"code": 200, "msg": "更新成功", "vehicle": vehicle.serialize()})

@vehicle_bp.route('/admin_delete_vehicles/<int:vehicle_id>', methods=['DELETE'])
# @role_required('admin')
@jwt_required()
def delete_vehicle(vehicle_id):
    vehicle = ElectricVehicle.query.get(vehicle_id)
    if not vehicle:
        return jsonify({"code": 404, "msg": "车辆不存在"}), 404
    db.session.delete(vehicle)
    db.session.commit()
    return jsonify({"code": 200, "msg": "删除成功"})

