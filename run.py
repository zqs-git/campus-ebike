from app import create_app  # 从app包导入工厂函数

app = create_app()  # 创建Flask应用实例


if __name__ == '__main__':

    # 打印关键配置验证
    # print("当前数据库URI:", app.config['SQLALCHEMY_DATABASE_URI'])
    # print("调试模式状态:", app.config['DEBUG'])
    # 启动开发服务器（调试模式建议通过环境变量控制）
    app.run(host='0.0.0.0', port=5000,debug=True)