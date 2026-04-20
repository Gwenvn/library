# 在线图书借阅管理系统

大专毕业设计项目 —— 基于 Flask + SQLite 实现的在线图书借阅管理系统。

---

## 项目结构

```
在线图书借阅管理系统/
├── app.py                  # 主程序，所有路由
├── config.py               # 配置文件
├── models.py               # 数据库模型
├── requirements.txt        # 依赖包列表
├── static/
│   ├── css/
│   │   └── style.css       # 自定义样式
│   └── images/             # 图书封面图片存放目录
│       └── default.jpg     # 默认封面（需自己放一张）
└── templates/
    ├── base.html           # 公共模板
    ├── login.html          # 用户登录
    ├── register.html       # 用户注册
    ├── index.html          # 首页
    ├── book_list.html      # 图书列表（含搜索）
    ├── book_detail.html    # 图书详情
    ├── my_borrow.html      # 我的借阅记录
    └── admin/
        ├── admin_login.html    # 管理员登录
        └── book_manage.html    # 图书管理（增删）
```

---

## 环境要求

- Python 3.8 及以上版本
- pip

---

## 安装步骤

### 第一步：安装依赖

打开命令提示符（cmd），进入项目目录，运行：

```bash
pip install -r requirements.txt
```

### 第二步：启动项目

```bash
python app.py
```

启动后访问：http://127.0.0.1:5000

---

## 如何创建管理员账号

项目启动后，在命令行中运行以下 Python 代码（另开一个终端）：

```bash
python
```

进入 Python 交互环境后，依次输入：

```python
from app import app, db
from models import User
from werkzeug.security import generate_password_hash

with app.app_context():
    admin = User(
        username='admin',
        email='admin@example.com',
        password=generate_password_hash('admin123'),
        is_admin=True
    )
    db.session.add(admin)
    db.session.commit()
    print('管理员创建成功')
```

然后访问 http://127.0.0.1:5000/admin/login，使用 `admin` / `admin123` 登录。

---

## 如何添加图书封面图片

1. 准备好图书封面图片（建议尺寸 200×280，JPG 或 PNG 格式）
2. 将图片复制到 `static/images/` 目录下，例如 `python.jpg`
3. 在管理后台添加图书时，"封面图片文件名"填写 `python.jpg` 即可
4. 如果不填，系统会使用默认封面 `default.jpg`

> 提示：`default.jpg` 需要自己放一张默认图片到 `static/images/` 目录，
> 否则无图书封面时页面会显示损坏图片图标。

---

## 功能说明

| 功能 | 说明 |
|------|------|
| 用户注册/登录 | 密码加密存储，使用 session 保持登录状态 |
| 图书浏览 | 首页展示最新6本，图书列表展示全部 |
| 搜索图书 | 支持按书名或作者模糊搜索 |
| 借书 | 登录后可借，自动检查库存，同一本书不能重复借 |
| 还书 | 在"我的借阅"页面点击还书，库存自动恢复 |
| 管理后台 | 管理员可添加图书、删除图书 |

---

## 技术栈

- 后端：Python Flask 2.3
- 数据库：SQLite + Flask-SQLAlchemy
- 前端：HTML5 + Bootstrap 5 + Bootstrap Icons
- 登录认证：Flask Session
