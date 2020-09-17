from sqlalchemy import Column, Integer, String, ForeignKey, Text, Float
from flask_login import UserMixin
from app.database import Base
from sqlalchemy.orm import relationship


class User(Base, UserMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    password = Column(String(120), unique=False)

    def __init__(self, name=None, password=None):
        self.name = name
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.name
