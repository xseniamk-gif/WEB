
import datetime
import sqlalchemy
from sqlalchemy import orm
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .db_session import SqlAlchemyBase


class Users(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    login = sqlalchemy.Column(sqlalchemy.String, nullable=True, unique=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    number = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    about = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String, nullable=True, unique=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    user_type_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users_types.id"))

    cart_items = orm.relationship('CartItem', back_populates='user', cascade='all, delete-orphan')
    user_type_rel = orm.relationship('UsersTypes', back_populates='users')

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)



class CartItem(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'cart_items'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'), nullable=False)
    tour_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('tours.id'), nullable=False)
    quantity = sqlalchemy.Column(sqlalchemy.Integer, default=1)
    added_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    user = orm.relationship('Users', back_populates='cart_items')
    tour = orm.relationship('Tours', back_populates='cart_items')  # Было 'tours', стало 'tour'


class UsersTypes(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'users_types'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    users_type = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    users = orm.relationship('Users', back_populates='user_type_rel')