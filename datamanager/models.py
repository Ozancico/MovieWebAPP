from sqlalchemy import Column, Integer, String, ForeignKey, Float, Text
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class User(Base):
    """
    SQLAlchemy User model representing a user in the database.
    """
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    movies = relationship(
        'Movie',
        back_populates='user',
        cascade='all, delete-orphan')
    reviews = relationship(
        'Review',
        back_populates='user',
        cascade='all, delete-orphan')


class Movie(Base):
    """
    SQLAlchemy Movie model representing a movie in the database.
    """
    __tablename__ = 'movies'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    director = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    rating = Column(Float, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='movies')
    reviews = relationship(
        'Review',
        back_populates='movie',
        cascade='all, delete-orphan')
    # OMDb Felder
    omdb_poster = Column(String, nullable=True)
    omdb_rating = Column(String, nullable=True)
    omdb_director = Column(String, nullable=True)
    omdb_year = Column(String, nullable=True)


class Review(Base):
    """
    SQLAlchemy Review model representing a review in the database.
    """
    __tablename__ = 'reviews'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    movie_id = Column(Integer, ForeignKey('movies.id'), nullable=False)
    review_text = Column(Text, nullable=False)
    rating = Column(Float, nullable=False)

    user = relationship('User', back_populates='reviews')
    movie = relationship('Movie', back_populates='reviews')
