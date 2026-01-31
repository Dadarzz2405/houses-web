from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
db = SQLAlchemy()

class Admin(db.Model, UserMixin):
    __tablename__ = 'admins'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    point_transactions = db.relationship(
        'PointTransaction', back_populates='admin'
    )

    def __repr__(self):
        return f'<Admin {self.username}>'


class House(db.Model):
    __tablename__ = 'houses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    house_points = db.Column(db.Integer, default=0)

    members = db.relationship('Member', back_populates='house')
    captains = db.relationship('Captain', back_populates='house')
    advisors = db.relationship('Advisor', back_populates='house')
    achievements = db.relationship('Achievement', back_populates='house')
    announcements = db.relationship('Announcement', back_populates='house')
    point_transactions = db.relationship('PointTransaction', back_populates='house')

    def __repr__(self):
        return f'<House {self.name}>'


class Captain(db.Model, UserMixin):
    __tablename__ = 'captains'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    house_id = db.Column(db.Integer, db.ForeignKey('houses.id'), nullable=False)
    house = db.relationship('House', back_populates='captains')

    announcements = db.relationship('Announcement', back_populates='captain')

    def __repr__(self):
        return f'<Captain {self.username}>'


class Member(db.Model):
    __tablename__ = 'members'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(150), nullable=False)

    house_id = db.Column(db.Integer, db.ForeignKey('houses.id'), nullable=False)
    house = db.relationship('House', back_populates='members')

    def __repr__(self):
        return f'<Member {self.name}>'


class Advisor(db.Model):
    __tablename__ = 'advisors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(150), nullable=False)
    bio = db.Column(db.Text)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    house_id = db.Column(db.Integer, db.ForeignKey('houses.id'), nullable=False)
    house = db.relationship('House', back_populates='advisors')

    def __repr__(self):
        return f'<Advisor {self.name}>'


class Achievement(db.Model):
    __tablename__ = 'achievements'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)

    house_id = db.Column(db.Integer, db.ForeignKey('houses.id'), nullable=False)
    house = db.relationship('House', back_populates='achievements')

    def __repr__(self):
        return f'<Achievement {self.name}>'


class Announcement(db.Model):
    __tablename__ = 'announcements'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )
    house_id = db.Column(db.Integer, db.ForeignKey('houses.id'), nullable=False)
    captain_id = db.Column(db.Integer, db.ForeignKey('captains.id'), nullable=True)

    house = db.relationship('House', back_populates='announcements')
    captain = db.relationship('Captain', back_populates='announcements')

    def __repr__(self):
        return f'<Announcement {self.title}>'


class PointTransaction(db.Model):
    __tablename__ = 'point_transactions'

    id = db.Column(db.Integer, primary_key=True)
    points_change = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(255), nullable=False)

    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    house_id = db.Column(db.Integer, db.ForeignKey('houses.id'), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('admins.id'), nullable=True)

    house = db.relationship('House', back_populates='point_transactions')
    admin = db.relationship('Admin', back_populates='point_transactions')
    def __repr__(self):
        return f'<PointTransaction {self.points_change}>'
