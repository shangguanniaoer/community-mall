from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, IntegerField, TextAreaField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, NumberRange

class LoginForm(FlaskForm):
    """管理员登录表单"""
    username = StringField('用户名', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('密码', validators=[DataRequired()])
    submit = SubmitField('登录')

class ProductForm(FlaskForm):
    """商品添加/编辑表单"""
    name = StringField('商品名称', validators=[DataRequired(), Length(max=100)])
    price = FloatField('价格', validators=[DataRequired(), NumberRange(min=0)])
    stock = IntegerField('库存', validators=[DataRequired(), NumberRange(min=0)])
    is_available = BooleanField('是否上架')
    description = TextAreaField('商品描述')
    submit = SubmitField('提交')

class OrderForm(FlaskForm):
    """订单表单"""
    name = StringField('姓名', validators=[DataRequired(), Length(max=100)])
    phone = StringField('电话', validators=[DataRequired(), Length(max=20)])
    address = StringField('地址', validators=[DataRequired(), Length(max=255)])
    community = StringField('所属小区', validators=[DataRequired(), Length(max=100)])
    is_group = BooleanField('参与拼单')
    submit = SubmitField('提交订单')
