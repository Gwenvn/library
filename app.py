from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from models import db, User, Book, BorrowRecord, Comment
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# ==================== 首页 ====================

@app.route('/')
def index():
    books = Book.query.order_by(Book.created_at.desc()).limit(8).all()
    total_books = Book.query.count()
    total_users = User.query.filter_by(is_admin=False).count()
    total_borrows = BorrowRecord.query.count()
    return render_template('index.html', books=books,
                           total_books=total_books,
                           total_users=total_users,
                           total_borrows=total_borrows)


# ==================== 用户注册登录 ====================

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        confirm  = request.form.get('confirm', '').strip()

        if not username or not email or not password:
            flash('请填写完整信息', 'danger')
            return redirect(url_for('register'))
        if password != confirm:
            flash('两次密码不一致', 'danger')
            return redirect(url_for('register'))
        if User.query.filter_by(username=username).first():
            flash('用户名已被注册', 'danger')
            return redirect(url_for('register'))
        if User.query.filter_by(email=email).first():
            flash('该邮箱已被注册', 'danger')
            return redirect(url_for('register'))

        new_user = User(username=username, email=email,
                        password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        flash('注册成功，请登录', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id']  = user.id
            session['username'] = user.username
            flash(f'欢迎回来，{user.username}！', 'success')
            return redirect(url_for('index'))
        else:
            flash('用户名或密码错误', 'danger')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('已退出登录', 'info')
    return redirect(url_for('index'))


# ==================== 用户个人中心 ====================

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('请先登录', 'warning')
        return redirect(url_for('login'))
    user = User.query.get_or_404(session['user_id'])
    # 统计数据
    total   = BorrowRecord.query.filter_by(user_id=user.id).count()
    current = BorrowRecord.query.filter_by(user_id=user.id, status='borrowed').count()
    done    = BorrowRecord.query.filter_by(user_id=user.id, status='returned').count()
    return render_template('profile.html', user=user,
                           total=total, current=current, done=done)


@app.route('/change_password', methods=['POST'])
def change_password():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    old_pw  = request.form.get('old_password', '').strip()
    new_pw  = request.form.get('new_password', '').strip()
    confirm = request.form.get('confirm_password', '').strip()

    user = User.query.get(session['user_id'])
    if not check_password_hash(user.password, old_pw):
        flash('原密码错误', 'danger')
        return redirect(url_for('profile'))
    if len(new_pw) < 4:
        flash('新密码至少4位', 'danger')
        return redirect(url_for('profile'))
    if new_pw != confirm:
        flash('两次新密码不一致', 'danger')
        return redirect(url_for('profile'))

    user.password = generate_password_hash(new_pw)
    db.session.commit()
    flash('密码修改成功，请重新登录', 'success')
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('login'))


# ==================== 图书 ====================

# 所有分类
CATEGORIES = ['全部', '计算机', 'Web开发', '数据库', '人工智能',
              '操作系统', '网络通信', '英语', '数学', '思政', '经管', '文学', '其他']

@app.route('/books')
def book_list():
    keyword  = request.args.get('keyword', '').strip()
    category = request.args.get('category', '全部')

    query = Book.query
    if keyword:
        query = query.filter(
            (Book.title.like(f'%{keyword}%')) | (Book.author.like(f'%{keyword}%'))
        )
    if category and category != '全部':
        query = query.filter_by(category=category)

    books = query.order_by(Book.created_at.desc()).all()
    return render_template('book_list.html', books=books,
                           keyword=keyword, category=category,
                           categories=CATEGORIES)


@app.route('/book/<int:book_id>')
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    comments = Comment.query.filter_by(book_id=book_id)\
                             .order_by(Comment.created_at.desc()).all()
    # 当前用户是否已评论过
    already_commented = False
    if 'user_id' in session:
        already_commented = Comment.query.filter_by(
            user_id=session['user_id'], book_id=book_id).first() is not None
    return render_template('book_detail.html', book=book,
                           comments=comments,
                           already_commented=already_commented)


@app.route('/borrow/<int:book_id>')
def borrow_book(book_id):
    if 'user_id' not in session:
        flash('请先登录', 'warning')
        return redirect(url_for('login'))

    book = Book.query.get_or_404(book_id)
    if book.stock <= 0:
        flash('库存不足，暂时无法借阅', 'warning')
        return redirect(url_for('book_detail', book_id=book_id))

    existing = BorrowRecord.query.filter_by(
        user_id=session['user_id'], book_id=book_id, status='borrowed').first()
    if existing:
        flash('你已经借了这本书，请先归还', 'warning')
        return redirect(url_for('book_detail', book_id=book_id))

    record = BorrowRecord(user_id=session['user_id'], book_id=book_id)
    book.stock -= 1
    db.session.add(record)
    db.session.commit()
    flash(f'《{book.title}》借阅成功！', 'success')
    return redirect(url_for('my_borrow'))


@app.route('/return/<int:record_id>')
def return_book(record_id):
    if 'user_id' not in session:
        flash('请先登录', 'warning')
        return redirect(url_for('login'))

    record = BorrowRecord.query.get_or_404(record_id)
    if record.user_id != session['user_id']:
        flash('操作无效', 'danger')
        return redirect(url_for('my_borrow'))
    if record.status == 'returned':
        flash('该书已归还', 'info')
        return redirect(url_for('my_borrow'))

    record.status      = 'returned'
    record.return_date = datetime.now()
    record.book.stock += 1
    db.session.commit()
    flash(f'《{record.book.title}》已成功归还！', 'success')
    return redirect(url_for('my_borrow'))


@app.route('/my_borrow')
def my_borrow():
    if 'user_id' not in session:
        flash('请先登录', 'warning')
        return redirect(url_for('login'))
    records = BorrowRecord.query.filter_by(user_id=session['user_id'])\
                                .order_by(BorrowRecord.borrow_date.desc()).all()
    return render_template('my_borrow.html', records=records)


# ==================== 评论 ====================

@app.route('/comment/<int:book_id>', methods=['POST'])
def add_comment(book_id):
    if 'user_id' not in session:
        flash('请先登录后再评论', 'warning')
        return redirect(url_for('login'))

    content = request.form.get('content', '').strip()
    rating  = int(request.form.get('rating', 5))

    if not content:
        flash('评论内容不能为空', 'danger')
        return redirect(url_for('book_detail', book_id=book_id))

    # 每人每本书只能评论一次
    if Comment.query.filter_by(user_id=session['user_id'], book_id=book_id).first():
        flash('你已经评论过这本书了', 'warning')
        return redirect(url_for('book_detail', book_id=book_id))

    c = Comment(user_id=session['user_id'], book_id=book_id,
                content=content, rating=max(1, min(5, rating)))
    db.session.add(c)
    db.session.commit()
    flash('评论发表成功！', 'success')
    return redirect(url_for('book_detail', book_id=book_id))


@app.route('/comment/delete/<int:comment_id>')
def delete_comment(comment_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    c = Comment.query.get_or_404(comment_id)
    if c.user_id != session['user_id']:
        flash('无权删除', 'danger')
        return redirect(url_for('book_detail', book_id=c.book_id))
    book_id = c.book_id
    db.session.delete(c)
    db.session.commit()
    flash('评论已删除', 'info')
    return redirect(url_for('book_detail', book_id=book_id))


# ==================== 管理员 ====================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        user = User.query.filter_by(username=username, is_admin=True).first()
        if user and check_password_hash(user.password, password):
            session['admin_id']   = user.id
            session['admin_name'] = user.username
            flash('管理员登录成功', 'success')
            return redirect(url_for('admin_books'))
        else:
            flash('账号或密码错误，或不是管理员账号', 'danger')
    return render_template('admin/admin_login.html')


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)
    session.pop('admin_name', None)
    flash('已退出管理后台', 'info')
    return redirect(url_for('admin_login'))


@app.route('/admin/books')
def admin_books():
    if 'admin_id' not in session:
        flash('请先登录管理后台', 'warning')
        return redirect(url_for('admin_login'))
    books = Book.query.order_by(Book.created_at.desc()).all()
    return render_template('admin/book_manage.html', books=books,
                           categories=CATEGORIES[1:])


@app.route('/admin/book/add', methods=['POST'])
def admin_add_book():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    title       = request.form.get('title', '').strip()
    author      = request.form.get('author', '').strip()
    publisher   = request.form.get('publisher', '').strip()
    isbn        = request.form.get('isbn', '').strip() or None
    description = request.form.get('description', '').strip()
    cover_image = request.form.get('cover_image', '').strip() or 'default.jpg'
    stock       = int(request.form.get('stock', 1))
    category    = request.form.get('category', '其他')

    if not title or not author:
        flash('书名和作者不能为空', 'danger')
        return redirect(url_for('admin_books'))

    db.session.add(Book(title=title, author=author, publisher=publisher,
                        isbn=isbn, description=description,
                        cover_image=cover_image, stock=stock, category=category))
    db.session.commit()
    flash(f'图书《{title}》添加成功', 'success')
    return redirect(url_for('admin_books'))


@app.route('/admin/book/delete/<int:book_id>')
def admin_delete_book(book_id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    book = Book.query.get_or_404(book_id)
    BorrowRecord.query.filter_by(book_id=book_id).delete()
    Comment.query.filter_by(book_id=book_id).delete()
    db.session.delete(book)
    db.session.commit()
    flash(f'图书《{book.title}》已删除', 'success')
    return redirect(url_for('admin_books'))


@app.route('/admin/borrows')
def admin_borrows():
    """管理员查看所有借阅记录"""
    if 'admin_id' not in session:
        flash('请先登录管理后台', 'warning')
        return redirect(url_for('admin_login'))

    status   = request.args.get('status', 'all')
    keyword  = request.args.get('keyword', '').strip()

    query = BorrowRecord.query
    if status == 'borrowed':
        query = query.filter_by(status='borrowed')
    elif status == 'returned':
        query = query.filter_by(status='returned')

    records = query.order_by(BorrowRecord.borrow_date.desc()).all()

    # 关键词筛选（按用户名或书名）
    if keyword:
        records = [r for r in records
                   if keyword in r.user.username or keyword in r.book.title]

    total_borrowed = BorrowRecord.query.filter_by(status='borrowed').count()
    total_returned = BorrowRecord.query.filter_by(status='returned').count()

    return render_template('admin/borrow_records.html',
                           records=records, status=status, keyword=keyword,
                           total_borrowed=total_borrowed,
                           total_returned=total_returned)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print('数据库初始化完成')
    app.run(debug=True)
