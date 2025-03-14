# tests/test_auth.py
from app.models.users import User
def test_internal_registration(client):
    """测试校内人员注册"""
    response = client.post('/api/auth/register', json={
        "user_type": "internal",
        "school_id": "202310001",
        "password": "Test@123",
        "name": "李四"
    })
    assert response.status_code == 201
    assert response.json['data']['role'] == 'student'

def test_external_registration(client):
    """测试校外访客注册"""
    response = client.post('/api/auth/register', json={
        "user_type": "external",
        "id_card": "11010119900307783X",
        "license_plate": "京A12345",
        "password": "Test@123"
    })
    assert response.status_code == 201
    assert response.json['data']['expire_time'] is not None