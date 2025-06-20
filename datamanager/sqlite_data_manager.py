# datamanager/sqlite_data_manager.py

from flask_sqlalchemy import SQLAlchemy
from datamanager.data_manager_interface import DataManagerInterface
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    movies = relationship("Movie", back_populates="user", cascade="all, delete-orphan")

class Movie(Base):
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    director = Column(String)
    year = Column(Integer)
    rating = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="movies")

class SQLiteDataManager(DataManagerInterface):
    def __init__(self, db_file_name):
        self.engine = create_engine(f"sqlite:///{db_file_name}")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def get_all_users(self):
        session = self.Session()
        users = session.query(User).all()
        session.close()
        return users

    def get_user_movies(self, user_id):
        session = self.Session()
        movies = session.query(Movie).filter_by(user_id=user_id).all()
        session.close()
        return movies

    def add_user(self, name):
        session = self.Session()
        user = User(name=name)
        session.add(user)
        session.commit()
        session.close()

    def add_movie(self, user_id, name, director, year, rating):
        session = self.Session()
        movie = Movie(user_id=user_id, name=name, director=director, year=year, rating=rating)
        session.add(movie)
        session.commit()
        session.close()

    def update_movie(self, movie_id, name, director, year, rating):
        session = self.Session()
        movie = session.query(Movie).filter_by(id=movie_id).first()
        if movie:
            movie.name = name
            movie.director = director
            movie.year = year
            movie.rating = rating
            session.commit()
        session.close()

    def delete_movie(self, movie_id):
        session = self.Session()
        movie = session.query(Movie).filter_by(id=movie_id).first()
        if movie:
            session.delete(movie)
            session.commit()
        session.close()
