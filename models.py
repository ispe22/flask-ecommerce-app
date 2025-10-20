from app import db 
from flask_login import UserMixin
import os
from decimal import Decimal


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f'<User {self.email}>'


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)  
    image_url = db.Column(db.String(255), nullable=True)
    stock_quantity = db.Column(db.Integer, default=0)

    # Create price_with_tax column
    @property
    def price_with_tax(self):
        tax_rate = float(os.getenv('TAX_RATE_MULTIPLIER', 1.255))
        return self.price * Decimal(tax_rate)

    def __repr__(self):
        return f'<Product {self.name}>'


class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)

    # Relationship to User and Product
    user = db.relationship('User', backref='cart_items')
    product = db.relationship('Product') 

    def __repr__(self):
        return f'<CartItem {self.quantity} x {self.product.name}>'


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  
    guest_email = db.Column(db.String(100), nullable=True) 
    order_date = db.Column(db.DateTime, server_default=db.func.now())
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    stripe_payment_id = db.Column(db.String(255), nullable=True) 
    status = db.Column(db.String(50), default='Pending')  

    # Relationship to User (can be null)
    user = db.relationship('User', backref='orders')

    def __repr__(self):
        return f'<Order {self.id}>'


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_purchase = db.Column(db.Numeric(10, 2), nullable=False)  

    # Relationship to Order and Product
    order = db.relationship('Order', backref='order_items') 
    product = db.relationship('Product')

    def __repr__(self):
        return f'<OrderItem {self.quantity} x {self.product.name} at {self.price_at_purchase}>'


# Extra, not used
class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    street = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    zip_code = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(100), nullable=False)

    # Relationship
    user = db.relationship('User', backref='addresses')

    def __repr__(self):
        return f'<Address {self.street}, {self.city}>'