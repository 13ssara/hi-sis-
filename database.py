from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
from werkzeug.security import generate_password_hash, check_password_hash

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)

class Thread(Base):
    __tablename__ = 'threads'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    content = Column(String(5000), default='')
    author = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    
    posts = relationship('Post', backref='thread', cascade='all, delete-orphan')

class Post(Base):
    __tablename__ = 'posts'
    
    id = Column(Integer, primary_key=True)
    thread_id = Column(Integer, ForeignKey('threads.id'), nullable=False)
    content = Column(String(5000), nullable=False)
    author = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

# Database setup
engine = None
Session = None

def init_db(app):
    global engine, Session
    db_path = app.config.get('DATABASE', 'reddit.db')
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

def get_db():
    return Session()
