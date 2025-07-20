from datamanager.data_manager_interface import DataManagerInterface
from datamanager.models import User, Movie, Review, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from MovieWebAPP.utils import fetch_omdb_data


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
        try:
            session = self.Session()
            users = session.query(User).all()
            session.close()
            return users
        except Exception as e:
            print(f"Error while retrieving all users: {e}")
            return []

    def get_user_movies(self, user_id):
        """
        Retrieve all movies for a specific user.
        Args:
            user_id (int): The ID of the user.
        Returns:
            list: A list of Movie objects for the user.
        """
        try:
            session = self.Session()
            movies = session.query(Movie).filter_by(user_id=user_id).all()
            session.close()
            return movies
        except Exception as e:
            print(f"Error while retrieving movies for user {user_id}: {e}")
            return []

    def add_user(self, user):
        """
        Add a new user to the database, only if the name is unique.
        Args:
            user (dict): A dictionary containing user information.
        Returns:
            User: The created User object, or None if already exists.
        """
        try:
            session = self.Session()
            existing = session.query(User).filter_by(name=user['name']).first()
            if existing:
                session.close()
                return None
            new_user = User(name=user['name'])
            session.add(new_user)
            session.commit()
            session.close()
            return new_user
        except Exception as e:
            print(f"Error while adding a user: {e}")
            return None

    def add_movie(self, movie):
        """
        Add a new movie to the database, only if not already present for the user (same name and year).
        Args:
            movie (dict): A dictionary containing movie information.
        Returns:
            Movie: The created Movie object, or None if already exists for the user.
        """
        try:
            import requests
            import os
            session = self.Session()
            existing = session.query(Movie).filter_by(
                name=movie['name'], year=movie['year'], user_id=movie['user_id']).first()
            if existing:
                session.close()
                return None
            # OMDb-Daten abrufen
            omdb_poster = None
            omdb_rating = None
            omdb_director = None
            omdb_year = None
            data = fetch_omdb_data(movie['name'])
            if data:
                omdb_poster = data.get('poster', None)
                omdb_rating = data.get('rating', None)
                omdb_director = data.get('director', None)
                omdb_year = data.get('year', None)
            new_movie = Movie(
                name=movie['name'],
                director=movie['director'],
                year=movie['year'],
                rating=movie['rating'],
                user_id=movie['user_id'],
                omdb_poster=omdb_poster,
                omdb_rating=omdb_rating,
                omdb_director=omdb_director,
                omdb_year=omdb_year
            )
            session.add(new_movie)
            session.commit()
            session.close()
            return new_movie
        except Exception as e:
            print(f"Error while adding a movie: {e}")
            return None

    def update_movie(self, movie):
        """
        Update an existing movie in the database.
        Args:
            movie (dict): A dictionary containing updated movie information.
        Returns:
            Movie: The updated Movie object, or None if not found.
        """
        try:
            import requests
            import os
            session = self.Session()
            db_movie = session.query(Movie).filter_by(id=movie['id']).first()
            if db_movie:
                db_movie.name = movie['name']
                db_movie.director = movie['director']
                db_movie.year = movie['year']
                db_movie.rating = movie['rating']
                # OMDb-Daten aktualisieren
                data = fetch_omdb_data(movie['name'])
                if data:
                    db_movie.omdb_poster = data.get('poster', None)
                    db_movie.omdb_rating = data.get('rating', None)
                    db_movie.omdb_director = data.get('director', None)
                    db_movie.omdb_year = data.get('year', None)
                session.commit()
            session.close()
            return db_movie
        except Exception as e:
            print(f"Error while updating a movie: {e}")
            return None

    def delete_movie(self, movie_id):
        """
        Delete a movie from the database.
        Args:
            movie_id (int): The ID of the movie to delete.
        Returns:
            Movie: The deleted Movie object, or None if not found.
        """
        try:
            session = self.Session()
            movie = session.query(Movie).filter_by(id=movie_id).first()
            if movie:
                session.delete(movie)
                session.commit()
            session.close()
            return movie
        except Exception as e:
            print(f"Error while deleting a movie: {e}")
            return None

    def add_review(self, review):
        """
        Add a new review to the database.
        Args:
            review (dict): A dictionary containing review information.
        Returns:
            Review: The created Review object.
        """
        try:
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
        except Exception as e:
            print(f"Error while adding a review: {e}")
            return None

    def get_reviews_for_movie(self, movie_id):
        """
        Retrieve all reviews for a specific movie.
        Args:
            movie_id (int): The ID of the movie.
        Returns:
            list: A list of Review objects for the movie.
        """
        try:
            session = self.Session()
            reviews = session.query(Review).filter_by(movie_id=movie_id).all()
            session.close()
            return reviews
        except Exception as e:
            print(f"Error while retrieving reviews for movie {movie_id}: {e}")
            return []

    def get_reviews_for_user(self, user_id):
        """
        Retrieve all reviews written by a specific user.
        Args:
            user_id (int): The ID of the user.
        Returns:
            list: A list of Review objects by the user.
        """
        try:
            session = self.Session()
            reviews = session.query(Review).filter_by(user_id=user_id).all()
            session.close()
            return reviews
        except Exception as e:
            print(f"Error while retrieving reviews for user {user_id}: {e}")
            return []

    def update_review(self, review):
        """
        Update an existing review in the database.
        Args:
            review (dict): A dictionary containing updated review information.
        Returns:
            Review: The updated Review object, or None if not found.
        """
        try:
            session = self.Session()
            db_review = session.query(Review).filter_by(
                id=review['id']).first()
            if db_review:
                db_review.review_text = review['review_text']
                db_review.rating = review['rating']
                session.commit()
            session.close()
            return db_review
        except Exception as e:
            print(f"Error while updating a review: {e}")
            return None

    def delete_review(self, review_id):
        """
        Delete a review from the database.
        Args:
            review_id (int): The ID of the review to delete.
        Returns:
            Review: The deleted Review object, or None if not found.
        """
        try:
            session = self.Session()
            review = session.query(Review).filter_by(id=review_id).first()
            if review:
                session.delete(review)
                session.commit()
            session.close()
            return review
        except Exception as e:
            print(f"Error while deleting a review: {e}")
            return None

    def search_movies(self, query):
        """
        Search for movies by title, director, or year (fuzzy, case-insensitive).
        Args:
            query (str): Search term
        Returns:
            list: List of Movie objects
        """
        try:
            session = self.Session()
            like_query = f"%{query}%"
            movies = session.query(Movie).filter(
                (Movie.name.ilike(like_query)) |
                (Movie.director.ilike(like_query)) |
                (Movie.year.ilike(like_query))
            ).all()
            session.close()
            return movies
        except Exception as e:
            print(f"Error while searching for movies: {e}")
            return []

    def get_all_movies(self):
        """
        Retrieve all movies from the database (global).
        Returns:
            list: List of all Movie objects
        """
        try:
            session = self.Session()
            movies = session.query(Movie).all()
            session.close()
            return movies
        except Exception as e:
            print(f"Error while retrieving all movies: {e}")
            return []
