import datetime

import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import check_password_hash, generate_password_hash

from .db_session import SqlAlchemyBase


class Users(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True,
                           autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String,
                             nullable=True)

    email = sqlalchemy.Column(sqlalchemy.String,
                              index=True,
                              unique=True,
                              nullable=True)
    user_type_id = sqlalchemy.Column(sqlalchemy.Integer,
                                     sqlalchemy.ForeignKey('users_types.id'),
                                     default=2,
                                     nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String,
                                        nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    basket = sqlalchemy.Column(sqlalchemy.Integer,
                              sqlalchemy.ForeignKey('tours.id'),
                              index=True,
                              unique=False,
                              nullable=True)
    history = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey('tours.id'),
                                index=True,
                                unique=False,
                                nullable=True)
    # back_populates должно указывать не на таблицу, а на атрибут класса orm.relationship
    tours = orm.relationship("Tours", back_populates='user')
    users_type = orm.relationship("UsersTypes", back_populates='user')

    # устанавливает значение хэша пароля для переданной строки.
    # для регистрации пользователя
    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    # правильный ли пароль ввел пользователь
    # авторизация пользователей
    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def __repr__(self):
        return f"***\n<class={__class__.__name__}>\n" \
               f"id={self.id}\tname={self.name}\tlogin={self.login}\temail={self.email}\tcreated_date={self.created_date}\n" \
               f"hashed_password={self.hashed_password}" \
               f"\n***"


class UsersTypes(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users_types'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True,
                           autoincrement=True)
    users_type = sqlalchemy.Column(sqlalchemy.Integer,
                                   nullable=True)

    user = orm.relationship("Users", back_populates='users_type')

    def __repr__(self):
        return f"***\n<class={__class__.__name__}>\n" \
               f"id={self.id}\tusers_type={self.users_type}\tuser={self.user}" \
               f"\n***"
