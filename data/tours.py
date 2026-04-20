import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Category(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'category'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True,
                           autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String,
                             nullable=True)
    tours = orm.relationship("Tours", cascade="all, delete", back_populates='category')


class Tours(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'tours'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    category_id = sqlalchemy.Column(sqlalchemy.Integer,
                                    sqlalchemy.ForeignKey("category.id"))
    title = sqlalchemy.Column(sqlalchemy.String,
                              nullable=True)
    content = sqlalchemy.Column(sqlalchemy.TEXT,
                                nullable=True)
    is_published = sqlalchemy.Column(sqlalchemy.Boolean,
                                     default=True)
    free_pl = sqlalchemy.Column(sqlalchemy.Integer)
    duration = sqlalchemy.Column(sqlalchemy.Integer, default=3)
    price = sqlalchemy.Column(sqlalchemy.Integer, default=10000)
    img = sqlalchemy.Column(sqlalchemy.String,
                            nullable=False)

    # Внешний ключ на таблицу users
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))

    # Связи
    category = orm.relationship("Category", back_populates='tours')
    # ИСПРАВЛЕНО: back_populates должен указывать на 'tour' (единственное число)
    cart_items = orm.relationship('CartItem', back_populates='tour', cascade='all, delete-orphan')
    author = orm.relationship("Users", foreign_keys=[user_id], backref='created_tours')

    def __repr__(self):
        return f"***\n<class={__class__.__name__}>\n" \
               f"id={self.id}\ttitle={self.title}\tcontent={self.content[:50] if self.content else ''}... " \
               f"\tis_published={self.is_published} " \
               f"\tcategory={self.category.name if self.category else None}" \
               f"\n***"