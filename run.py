from app import create_app

app = create_app()

if __name__ == '__main__':
    # 打印关键配置验证
    print("当前数据库URI:", app.config['SQLALCHEMY_DATABASE_URI'])
    print("调试模式状态:", app.config['DEBUG'])
    app.run(host='0.0.0.0', port=5000)