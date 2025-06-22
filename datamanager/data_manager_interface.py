from abc import ABC, abstractmethod

class DataManagerInterface(ABC):
    """
    Interface for data management classes. Defines the required methods for any data manager implementation.
    """
    @abstractmethod
    def get_all_users(self):
        """
        Retrieve all users from the data source.
        Returns:
            list: A list of user objects.
        """
        pass

    @abstractmethod
    def get_user_movies(self, user_id):
        """
        Retrieve all movies for a specific user.
        Args:
            user_id (int): The ID of the user.
        Returns:
            list: A list of movie objects for the user.
        """
        pass

    @abstractmethod
    def add_user(self, user):
        """
        Add a new user to the data source.
        Args:
            user (dict): A dictionary containing user information.
        Returns:
            object: The created user object.
        """
        pass

    @abstractmethod
    def add_movie(self, movie):
        """
        Add a new movie to the data source.
        Args:
            movie (dict): A dictionary containing movie information.
        Returns:
            object: The created movie object.
        """
        pass

    @abstractmethod
    def update_movie(self, movie):
        """
        Update an existing movie in the data source.
        Args:
            movie (dict): A dictionary containing updated movie information.
        Returns:
            object: The updated movie object.
        """
        pass

    @abstractmethod
    def delete_movie(self, movie_id):
        """
        Delete a movie from the data source.
        Args:
            movie_id (int): The ID of the movie to delete.
        Returns:
            object: The deleted movie object or None if not found.
        """
        pass

    @abstractmethod
    def add_review(self, review):
        """
        Add a new review to the data source.
        Args:
            review (dict): A dictionary containing review information.
        Returns:
            object: The created review object.
        """
        pass

    @abstractmethod
    def get_reviews_for_movie(self, movie_id):
        """
        Retrieve all reviews for a specific movie.
        Args:
            movie_id (int): The ID of the movie.
        Returns:
            list: A list of review objects for the movie.
        """
        pass

    @abstractmethod
    def get_reviews_for_user(self, user_id):
        """
        Retrieve all reviews written by a specific user.
        Args:
            user_id (int): The ID of the user.
        Returns:
            list: A list of review objects by the user.
        """
        pass

    @abstractmethod
    def update_review(self, review):
        """
        Update an existing review in the data source.
        Args:
            review (dict): A dictionary containing updated review information.
        Returns:
            object: The updated review object.
        """
        pass

    @abstractmethod
    def delete_review(self, review_id):
        """
        Delete a review from the data source.
        Args:
            review_id (int): The ID of the review to delete.
        Returns:
            object: The deleted review object or None if not found.
        """
        pass
