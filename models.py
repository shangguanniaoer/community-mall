from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# 初始化数据库连接
db = SQLAlchemy()

class Product(db.Model):
    """商品模型"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    is_available = db.Column(db.Boolean, nullable=False, default=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Product {self.name}>'

class Order(db.Model):
    """订单模型"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    community = db.Column(db.String(100), nullable=False)
    is_group = db.Column(db.Boolean, nullable=False, default=False)
    items = db.Column(db.JSON, nullable=False)  # 存储商品列表 [{product_id, quantity, price}]
    total_price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Order {self.id}>'
