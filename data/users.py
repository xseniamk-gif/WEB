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
    login = sqlalchemy.Column(sqlalchemy.String,
                              index=True,
                              unique=True,
                              nullable=True)
    name = sqlalchemy.Column(sqlalchemy.String,
                             nullable=True)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    number = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    about = sqlalchemy.Column(sqlalchemy.TEXT, nullable=True)
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

    # Внешние ключи на таблицу tours
    basket_id = sqlalchemy.Column(sqlalchemy.Integer,
                                  sqlalchemy.ForeignKey('tours.id'),
                                  nullable=True)
    history_id = sqlalchemy.Column(sqlalchemy.Integer,
                                   sqlalchemy.ForeignKey('tours.id'),
                                   nullable=True)

    # Связи с указанием foreign_keys
    basket_tour = orm.relationship("Tours", foreign_keys=[basket_id], backref="users_in_basket")
    history_tour = orm.relationship("Tours", foreign_keys=[history_id], backref="users_in_history")

    # Связь с типом пользователя (ИСПРАВЛЕНО!)
    user_type = orm.relationship("UsersTypes", back_populates='users')  # Изменено с users_type на user_type

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def __repr__(self):
        return f"***\n<class={__class__.__name__}>\n" \
               f"id={self.id}\tname={self.name}\tsurname={self.surname}\tlogin={self.login}\temail={self.email}\tcreated_date={self.created_date}\n" \
               f"hashed_password={self.hashed_password}" \
               f"\n***"


class UsersTypes(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users_types'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True,
                           autoincrement=True)
    users_type = sqlalchemy.Column(sqlalchemy.String,  # String, а не Integer!
                                   nullable=True)

    # Связь с пользователями (ИСПРАВЛЕНО!)
    users = orm.relationship("Users", back_populates='user_type')  # Изменено с user на users

    def __repr__(self):
        return f"***\n<class={__class__.__name__}>\n" \
               f"id={self.id}\tusers_type={self.users_type}" \
               f"\n***"