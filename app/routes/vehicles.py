import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models.users import User
from app.models.vehicles import ElectricVehicle
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.permissions import role_required  # 从权限模块导入
from flask_cors import cross_origin         # 导入跨域扩展
from app.utils.oss_util import upload_to_oss  # 导入OSS上传工具（若使用OSS上传）

vehicle_bp = Blueprint('vehicle', __name__, url_prefix='/api/vehicle')

# 绑定电动车接口
@vehicle_bp.route('/bind', methods=['POST','OPTIONS'])
@jwt_required()
def bind_vehicle():
    if request.method == "OPTIONS":
        return '', 200  # 返回空 200 响应即可
    print("🚀 进入 bind_vehicle")

    # 从 multipart/form-data 获取字段
    plate_number = request.form.get('plate_number')
    brand = request.form.get('brand')
    color = request.form.get('color')
    status = request.form.get('status', 'active')
    file = request.files.get('image')  # 获取上传的图片

    # 校验必要字段
    if not plate_number or not brand:
        return jsonify({"code": 400, "msg": "plate_number 和 brand 为必填项"}), 400

    # 获取当前用户
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 404, "msg": "用户不存在"}), 404

    # 检查是否已有绑定
    if ElectricVehicle.query.filter_by(owner_id=user_id).first():
        return jsonify({"code": 400, "msg": "该用户已绑定电动车"}), 400

    if ElectricVehicle.query.filter_by(plate_number=plate_number).first():
        return jsonify({"code": 400, "msg": "该车牌已被绑定"}), 400

    # 上传图片（如有）
    image_url = upload_to_oss(file) if file else None

    # 创建并绑定车辆
    new_vehicle = ElectricVehicle(
        plate_number=plate_number,
        brand=brand,
        color=color,
        status=status,
        owner_id=user_id,
        image_url=image_url
    )

    try:
        db.session.add(new_vehicle)
        db.session.commit()
        return jsonify({
            "code": 201,
            "msg": "电动车绑定成功",
            "vehicle": {
                "vehicle_id": new_vehicle.id,
                "plate_number": new_vehicle.plate_number,
                "brand": new_vehicle.brand,
                "color": new_vehicle.color,
                "status": new_vehicle.status,
                "owner_id": new_vehicle.owner_id,
                "image_url": new_vehicle.image_url
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "msg": "电动车绑定失败", "details": str(e)}), 500


# 解绑电动车接口
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
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 404, "msg": "用户不存在"}), 404

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


# 更新电动车信息接口
@vehicle_bp.route('/update', methods=['PUT'])
@jwt_required()
def update_vehicle():
    """
    用户更新电动车信息接口，支持 multipart/form-data 格式（包括图片上传）
    """
    if request.content_type.startswith('multipart/form-data'):
        vehicle_id = request.form.get('vehicle_id')
        new_brand = request.form.get('brand')
        new_color = request.form.get('color')
        new_model = request.form.get('model')
        new_plate_number = request.form.get('plate_number')
        new_battery_capacity = request.form.get('battery_capacity')
        file = request.files.get('image')  # 新上传的图片
    else:
        return jsonify({"code": 400, "msg": "请求格式必须为 multipart/form-data"}), 400

    if not vehicle_id:
        return jsonify({"code": 400, "msg": "vehicle_id 为必填项"}), 400

    # 当前用户
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 404, "msg": "用户不存在"}), 404

    # 查询车辆
    vehicle = ElectricVehicle.query.filter_by(owner_id=user_id, id=vehicle_id).first()
    if not vehicle:
        return jsonify({"code": 404, "msg": "电动车不存在或不属于当前用户"}), 404

    # 处理字段更新
    if new_plate_number and new_plate_number != vehicle.plate_number:
        if ElectricVehicle.query.filter_by(plate_number=new_plate_number).first():
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

    # 处理图片更新（上传到 OSS）
    if file:
        image_url = upload_to_oss(file)
        vehicle.image_url = image_url

    try:
        db.session.commit()
        return jsonify({
            "code": 200,
            "msg": "电动车信息更新成功",
            "vehicle": vehicle.serialize()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "msg": "更新失败", "details": str(e)}), 500

# 获取当前用户绑定的电动车信息接口
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
            "status": vehicle.status,
            "owner_id": vehicle.owner_id,
            "image_url": vehicle.image_url,
        }
    }), 200


# 获取所有电动车信息接口（管理员专属）
@vehicle_bp.route('/admin_vehicle', methods=['GET'])
@jwt_required()
def get_all_vehicles():
    """获取所有车辆信息（管理员专属接口）"""
    vehicles = ElectricVehicle.query.all()
    return jsonify({
        "code": 200,
        "data": [vehicle.serialize() for vehicle in vehicles]
    }), 200



# 更新电动车信息接口（管理员专属）
@vehicle_bp.route('/admin_update_vehicles/<int:vehicle_id>', methods=['PUT'])
@jwt_required()
# @role_required('admin')
def admin_update_vehicles(vehicle_id):
    if request.content_type.startswith('multipart/form-data'):
        plate_number = request.form.get('plate_number')
        status = request.form.get('status')
        file = request.files.get('image')
    else:
        return jsonify({"code": 400, "msg": "请求格式必须为 multipart/form-data"}), 400

    vehicle = ElectricVehicle.query.get(vehicle_id)
    if not vehicle:
        return jsonify({"code": 404, "msg": "车辆不存在"}), 404

    if plate_number:
        vehicle.plate_number = plate_number
    if status:
        vehicle.status = status
    if file:
        image_url = upload_to_oss(file)
        vehicle.image_url = image_url

    try:
        db.session.commit()
        return jsonify({"code": 200, "msg": "更新成功", "vehicle": vehicle.serialize()})
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "msg": "更新失败", "details": str(e)}), 500

# 删除电动车接口（管理员专属）
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
