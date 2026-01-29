from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def __repr__(self):
        return f'<Admin {self.username}>'

class Captain(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    house_id = db.Column(db.Integer, db.ForeignKey('houses.id'), nullable=False)

    def __repr__(self):
        return f'<Captain {self.username} of House ID {self.house_id}>'

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(150), nullable=False)
    house_id = db.Column(db.Integer, db.ForeignKey('houses.id'), nullable=False)

    def __repr__(self):
        return f'<Member {self.name} - {self.role}>'

class Advisor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(150), nullable=False)
    bio = db.Column(db.Text)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    house_id = db.Column(db.Integer, db.ForeignKey('houses.id'), nullable=False)
    def __repr__(self):
        return f'<Advisor {self.name}>'

class House(db.Model):
    __tablename__ = 'houses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    house_points = db.Column(db.Integer, default=0)

    members = db.relationship('Member', backref='house', lazy=True)
    achievements = db.relationship('Achievement', backref='house', lazy=True)

    def __repr__(self):
        return f'<House {self.name}>'

class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    house_id = db.Column(db.Integer, db.ForeignKey('houses.id'), nullable=False)

    def __repr__(self):
        return f'<Achievement {self.name}>'
