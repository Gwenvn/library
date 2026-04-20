import os

# 基础配置
class Config:
    # 数据库文件路径（当前目录下的 library.db）
    SQLALCHEMY_DATABASE_URI = 'sqlite:///library.db'
    # 关闭 SQLAlchemy 的修改追踪，节省内存
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # session 加密密钥，实际部署时改成复杂字符串
    SECRET_KEY = 'library_secret_key_2024'
    # 上传图片保存路径
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'images')
