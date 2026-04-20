from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# 用户表
class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    borrow_records = db.relationship('BorrowRecord', backref='user', lazy=True)
    comments = db.relationship('Comment', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'


# 图书表
class Book(db.Model):
    __tablename__ = 'book'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(50), nullable=False)
    publisher = db.Column(db.String(100))
    isbn = db.Column(db.String(30), unique=True)
    description = db.Column(db.Text)
    cover_image = db.Column(db.String(200), default='default.jpg')
    stock = db.Column(db.Integer, default=1)
    category = db.Column(db.String(50), default='其他')   # 图书分类
    created_at = db.Column(db.DateTime, default=datetime.now)

    borrow_records = db.relationship('BorrowRecord', backref='book', lazy=True)
    comments = db.relationship('Comment', backref='book', lazy=True)

    def __repr__(self):
        return f'<Book {self.title}>'


# 借阅记录表
class BorrowRecord(db.Model):
    __tablename__ = 'borrow_record'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    borrow_date = db.Column(db.DateTime, default=datetime.now)
    return_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='borrowed')   # borrowed / returned

    def __repr__(self):
        return f'<BorrowRecord user={self.user_id} book={self.book_id}>'


# 评论表
class Comment(db.Model):
    __tablename__ = 'comment'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)             # 评论内容
    rating = db.Column(db.Integer, default=5)                # 评分 1-5
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f'<Comment user={self.user_id} book={self.book_id}>'
