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
    tours = orm.relationship("Tours", cascade="all, delete")


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
    reviews = sqlalchemy.Column(sqlalchemy.Integer,
                              nullable=True)
    category = orm.relationship("Category", back_populates='tours')


    def __repr__(self):
        return f"***\n<class={__class__.__name__}>\n" \
               f"id={self.id}\ttitle={self.title}\tcontent={self.content} " \
               f"\tis_published={self.is_published} " \
               f"\tcategories={self.category} " \
               f"\n***"


