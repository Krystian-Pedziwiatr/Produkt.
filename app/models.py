from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<Setting {self.key}={self.value}>"


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    sku = db.Column(db.String(50), unique=True, nullable=False)
    ean = db.Column(db.String(13), unique=True, nullable=True)
    description_template_pl = db.Column(db.Text, nullable=True)
    description_template_en = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    variants = db.relationship('Variant', backref='product', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Product {self.name}>'

class Variant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    color = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    image2_url = db.Column(db.String(255), nullable=True)
    image3_url = db.Column(db.String(255), nullable=True)
    image4_url = db.Column(db.String(255), nullable=True)
    image5_url = db.Column(db.String(255), nullable=True)
    image6_url = db.Column(db.String(255), nullable=True)
    image7_url = db.Column(db.String(255), nullable=True)
    image8_url = db.Column(db.String(255), nullable=True)
    image9_url = db.Column(db.String(255), nullable=True)
    image10_url = db.Column(db.String(255), nullable=True)
    link_url = db.Column(db.String(255), nullable=True)
    link2_url = db.Column(db.String(255), nullable=True)
    link3_url = db.Column(db.String(255), nullable=True)
    link4_url = db.Column(db.String(255), nullable=True)
    link5_url = db.Column(db.String(255), nullable=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

    def __repr__(self):
        return f'<Variant {self.id}>'

class Icon(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(1000), nullable=False)
    category = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Icon {self.name}>'

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "category": self.category,
        }
