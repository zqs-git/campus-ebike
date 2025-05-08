# run.py
from app import create_app  # 从app包导入工厂函数

app = create_app()  # 创建Flask应用实例

print("Registered Routes:")
for rule in app.url_map.iter_rules():
    print(f"{rule.endpoint}: {rule}")

if __name__ == '__main__':
    # 打印关键配置验证
    # print("当前数据库URI:", app.config['SQLALCHEMY_DATABASE_URI'])
    # print("调试模式状态:", app.config['DEBUG'])

    # app.run(host='0.0.0.0', port=5000, debug=True)
    
    # 如果使用 socketio，替换上面为：
    from app.extensions import socketio
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
