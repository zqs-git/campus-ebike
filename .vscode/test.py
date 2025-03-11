# flask_test.py

# 1. 导入Flask核心模块
from flask import Flask

# 2. 创建应用实例
app = Flask(__name__)

# 3. 定义根路由
@app.route('/')
def hello_world():
    # 4. 设置断点测试变量（在第8行左侧点击添加断点）
    greeting = "Hello, Flask Environment!"
    
    # 5. 返回响应内容
    return f"{greeting} 当前Python版本：{__import__('sys').version}"

# 6. 启动开发服务器
if __name__ == '__main__':
    # 开启调试模式（自动重载代码+显示错误详情）
    app.run(debug=True, port=5050)  # 指定5050端口避免冲突