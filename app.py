from flask import Flask, render_template, redirect, url_for, request, session, flash
from models import db, Product, Order
from forms import LoginForm, ProductForm, OrderForm
import os

# 初始化 Flask 应用
app = Flask(__name__)

# 配置密钥和数据库
app.config['SECRET_KEY'] = 'your-secret-key'
# 检查是否存在 DATABASE_URL 环境变量
if os.environ.get('DATABASE_URL'):
    # 使用环境变量中的数据库 URL
    # 处理 Render 等平台提供的 DATABASE_URL 格式（可能需要替换前缀）
    database_url = os.environ.get('DATABASE_URL')
    # 确保使用正确的 PostgreSQL 连接格式
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://')
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # 默认使用本地 SQLite
    # 确保 data 文件夹存在
    base_dir = os.path.abspath(os.path.dirname(__file__))
    data_dir = os.path.join(base_dir, 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    db_path = os.path.join(data_dir, 'community.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化数据库
db.init_app(app)

# 应用启动时创建数据库表
try:
    with app.app_context():
        db.create_all()
    print("数据库连接成功，表结构已创建")
except Exception as e:
    print(f"数据库连接失败: {str(e)}")
    # 继续运行应用，即使数据库连接失败

# 测试数据库连接
@app.route('/test-db')
def test_db():
    try:
        with app.app_context():
            # 测试数据库连接
            db.session.execute('SELECT 1')
        return "数据库连接正常"
    except Exception as e:
        print(f"数据库测试失败: {str(e)}")
        return f"数据库测试失败: {str(e)}"

# 全局错误处理
@app.errorhandler(500)
def internal_server_error(error):
    print(f"内部服务器错误: {str(error)}")
    return "内部服务器错误，请稍后再试", 500

# 404错误处理
@app.errorhandler(404)
def not_found_error(error):
    return "页面不存在", 404

# 检查是否需要创建初始管理员账号
# 这里简化处理，使用固定的账号密码：admin/123456

# 管理员登录验证装饰器
def login_required(f):
    def wrapper(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    # 为了避免端点函数名称冲突，设置与原函数相同的名称
    wrapper.__name__ = f.__name__
    return wrapper

# 管理员登录页面
@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        # 验证账号密码
        if username == 'admin' and password == '123456':
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('用户名或密码错误', 'danger')
    return render_template('admin/login.html', form=form)

# 管理员登出
@app.route('/admin/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('login'))

# 管理员仪表盘
@app.route('/admin')
@login_required
def admin_dashboard():
    return redirect(url_for('admin_products'))

# 管理员商品管理
@app.route('/admin/products', methods=['GET', 'POST'])
@login_required
def admin_products():
    try:
        products = Product.query.all()
    except Exception as e:
        print(f"获取商品列表失败: {str(e)}")
        products = []
    form = ProductForm()
    if form.validate_on_submit():
        try:
            # 打印表单数据，用于调试
            print(f"表单数据: name={form.name.data}, price={form.price.data}, stock={form.stock.data}, is_available={form.is_available.data}, description={form.description.data}")
            
            # 添加新商品
            product = Product(
                name=form.name.data,
                price=form.price.data,
                stock=form.stock.data,
                is_available=form.is_available.data,
                description=form.description.data
            )
            
            # 打印商品对象，用于调试
            print(f"商品对象: {product}")
            
            db.session.add(product)
            # 打印添加后的会话状态，用于调试
            print(f"会话状态: {db.session.new}")
            
            db.session.commit()
            # 打印提交后的会话状态，用于调试
            print(f"提交后会话状态: {db.session.new}")
            
            flash('商品添加成功', 'success')
            return redirect(url_for('admin_products'))
        except Exception as e:
            print(f"添加商品失败: {str(e)}")
            # 打印详细的错误信息，包括堆栈跟踪
            import traceback
            traceback.print_exc()
            flash('商品添加失败，请稍后再试', 'danger')
            db.session.rollback()
    return render_template('admin/products.html', products=products, form=form)

# 编辑商品
@app.route('/admin/products/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        form = ProductForm(obj=product)
        if form.validate_on_submit():
            try:
                product.name = form.name.data
                product.price = form.price.data
                product.stock = form.stock.data
                # 库存为0时自动下架
                if product.stock <= 0:
                    product.is_available = False
                else:
                    product.is_available = form.is_available.data
                product.description = form.description.data
                db.session.commit()
                flash('商品更新成功', 'success')
                return redirect(url_for('admin_products'))
            except Exception as e:
                print(f"更新商品失败: {str(e)}")
                flash('商品更新失败，请稍后再试', 'danger')
                db.session.rollback()
        return render_template('admin/edit_product.html', form=form, product=product)
    except Exception as e:
        print(f"获取商品详情失败: {str(e)}")
        return "商品不存在或已下架", 404

# 删除商品
@app.route('/admin/products/delete/<int:product_id>')
@login_required
def delete_product(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        try:
            db.session.delete(product)
            db.session.commit()
            flash('商品删除成功', 'success')
        except Exception as e:
            print(f"删除商品失败: {str(e)}")
            flash('商品删除失败，请稍后再试', 'danger')
            db.session.rollback()
    except Exception as e:
        print(f"获取商品详情失败: {str(e)}")
        flash('商品不存在或已下架', 'danger')
    return redirect(url_for('admin_products'))

# 管理员订单管理
@app.route('/admin/orders')
@login_required
def admin_orders():
    try:
        # 获取所有订单
        orders = Order.query.order_by(Order.created_at.desc()).all()
        # 按小区分组
        community_orders = {}
        import json
        for order in orders:
            # 将 items 字符串转换回 JSON 对象
            try:
                order.items = json.loads(order.items)
            except Exception as e:
                print(f"解析订单 items 失败: {str(e)}")
                order.items = []
            if order.community not in community_orders:
                community_orders[order.community] = []
            community_orders[order.community].append(order)
    except Exception as e:
        print(f"获取订单列表失败: {str(e)}")
        community_orders = {}
    return render_template('admin/orders.html', community_orders=community_orders)

# 用户端首页 - 展示上架商品
@app.route('/')
def home():
    try:
        # 只显示上架且库存大于0的商品
        products = Product.query.filter_by(is_available=True).filter(Product.stock > 0).all()
    except Exception as e:
        print(f"获取商品列表失败: {str(e)}")
        products = []
    return render_template('user/home.html', products=products)

# 用户端商品详情和下单页面
@app.route('/product/<int:product_id>', methods=['GET', 'POST'])
def product_detail(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        form = OrderForm()
        if form.validate_on_submit():
            try:
                # 创建订单
                import json
                order = Order(
                    name=form.name.data,
                    phone=form.phone.data,
                    address=form.address.data,
                    community=form.community.data,
                    is_group=form.is_group.data,
                    items=json.dumps([{'product_id': product.id, 'quantity': 1, 'price': product.price}]),
                    total_price=product.price
                )
                # 减少库存
                product.stock -= 1
                # 库存为0时自动下架
                if product.stock <= 0:
                    product.is_available = False
                db.session.add(order)
                db.session.commit()
                flash('订单提交成功', 'success')
                return redirect(url_for('home'))
            except Exception as e:
                print(f"提交订单失败: {str(e)}")
                flash('订单提交失败，请稍后再试', 'danger')
                db.session.rollback()
        return render_template('user/product_detail.html', product=product, form=form)
    except Exception as e:
        print(f"获取商品详情失败: {str(e)}")
        return "商品不存在或已下架", 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(debug=True, host='0.0.0.0', port=port)
