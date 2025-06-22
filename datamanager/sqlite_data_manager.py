from datamanager.data_manager_interface import DataManagerInterface
from sqlalchemy import Column, Integer, String, ForeignKey, Float, create_engine, Text
from sqlalchemy.orm import relationship, declarative_base, sessionmaker

Base = declarative_base()

class User(Base):
    """
    SQLAlchemy User model representing a user in the database.
    """
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    movies = relationship('Movie', back_populates='user')

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

    user = relationship('User')
    movie = relationship('Movie')

class SQLiteDataManager(DataManagerInterface):
    """
    Data manager implementation for SQLite using SQLAlchemy ORM.
    """
    def __init__(self, db_file_name):
        """
        Initialize the SQLiteDataManager with the given database file name.
        Args:
            db_file_name (str): The SQLite database file name.
        """
        self.engine = create_engine(f'sqlite:///{db_file_name}')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def get_all_users(self):
        """
        Retrieve all users from the database.
        Returns:
            list: A list of User objects.
        """
        session = self.Session()
        users = session.query(User).all()
        session.close()
        return users

    def get_user_movies(self, user_id):
        """
        Retrieve all movies for a specific user.
        Args:
            user_id (int): The ID of the user.
        Returns:
            list: A list of Movie objects for the user.
        """
        session = self.Session()
        movies = session.query(Movie).filter_by(user_id=user_id).all()
        session.close()
        return movies

    def add_user(self, user):
        """
        Add a new user to the database.
        Args:
            user (dict): A dictionary containing user information.
        Returns:
            User: The created User object.
        """
        session = self.Session()
        new_user = User(name=user['name'])
        session.add(new_user)
        session.commit()
        session.close()
        return new_user

    def add_movie(self, movie):
        """
        Add a new movie to the database.
        Args:
            movie (dict): A dictionary containing movie information.
        Returns:
            Movie: The created Movie object.
        """
        session = self.Session()
        new_movie = Movie(
            name=movie['name'],
            director=movie['director'],
            year=movie['year'],
            rating=movie['rating'],
            user_id=movie['user_id']
        )
        session.add(new_movie)
        session.commit()
        session.close()
        return new_movie

    def update_movie(self, movie):
        """
        Update an existing movie in the database.
        Args:
            movie (dict): A dictionary containing updated movie information.
        Returns:
            Movie: The updated Movie object, or None if not found.
        """
        session = self.Session()
        db_movie = session.query(Movie).filter_by(id=movie['id']).first()
        if db_movie:
            db_movie.name = movie['name']
            db_movie.director = movie['director']
            db_movie.year = movie['year']
            db_movie.rating = movie['rating']
            session.commit()
        session.close()
        return db_movie

    def delete_movie(self, movie_id):
        """
        Delete a movie from the database.
        Args:
            movie_id (int): The ID of the movie to delete.
        Returns:
            Movie: The deleted Movie object, or None if not found.
        """
        session = self.Session()
        movie = session.query(Movie).filter_by(id=movie_id).first()
        if movie:
            session.delete(movie)
            session.commit()
        session.close()
        return movie

    def add_review(self, review):
        """
        Add a new review to the database.
        Args:
            review (dict): A dictionary containing review information.
        Returns:
            Review: The created Review object.
        """
        session = self.Session()
        new_review = Review(
            user_id=review['user_id'],
            movie_id=review['movie_id'],
            review_text=review['review_text'],
            rating=review['rating']
        )
        session.add(new_review)
        session.commit()
        session.close()
        return new_review

    def get_reviews_for_movie(self, movie_id):
        """
        Retrieve all reviews for a specific movie.
        Args:
            movie_id (int): The ID of the movie.
        Returns:
            list: A list of Review objects for the movie.
        """
        session = self.Session()
        reviews = session.query(Review).filter_by(movie_id=movie_id).all()
        session.close()
        return reviews

    def get_reviews_for_user(self, user_id):
        """
        Retrieve all reviews written by a specific user.
        Args:
            user_id (int): The ID of the user.
        Returns:
            list: A list of Review objects by the user.
        """
        session = self.Session()
        reviews = session.query(Review).filter_by(user_id=user_id).all()
        session.close()
        return reviews

    def update_review(self, review):
        """
        Update an existing review in the database.
        Args:
            review (dict): A dictionary containing updated review information.
        Returns:
            Review: The updated Review object, or None if not found.
        """
        session = self.Session()
        db_review = session.query(Review).filter_by(id=review['id']).first()
        if db_review:
            db_review.review_text = review['review_text']
            db_review.rating = review['rating']
            session.commit()
        session.close()
        return db_review

    def delete_review(self, review_id):
        """
        Delete a review from the database.
        Args:
            review_id (int): The ID of the review to delete.
        Returns:
            Review: The deleted Review object, or None if not found.
        """
        session = self.Session()
        review = session.query(Review).filter_by(id=review_id).first()
        if review:
            session.delete(review)
            session.commit()
        session.close()
        return review
