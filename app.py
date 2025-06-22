from flask import Flask, render_template, request, redirect, url_for
from datamanager.sqlite_data_manager import SQLiteDataManager
import requests

app = Flask(__name__)
data_manager = SQLiteDataManager('moviwebapp.db')

@app.route('/')
def home():
    """
    Render the home page of the MovieWeb App.
    """
    return render_template('home.html')

@app.route('/users')
def list_users():
    """
    Display a list of all users.
    """
    users = data_manager.get_all_users()
    return render_template('users.html', users=users)

@app.route('/users/<int:user_id>')
def user_movies(user_id):
    """
    Display a list of movies for a specific user.
    Args:
        user_id (int): The ID of the user.
    """
    movies = data_manager.get_user_movies(user_id)
    return render_template('movies.html', movies=movies, user_id=user_id)

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    """
    Display a form to add a new user and handle form submission.
    """
    if request.method == 'POST':
        name = request.form['name']
        data_manager.add_user({'name': name})
        return redirect(url_for('list_users'))
    return render_template('add_user.html')

@app.route('/users/<int:user_id>/add_movie', methods=['GET', 'POST'])
def add_movie(user_id):
    """
    Display a form to add a new movie for a user, handle OMDb API lookup and form submission.
    Args:
        user_id (int): The ID of the user.
    """
    omdb_data = None
    error = None
    try:
        if request.method == 'POST':
            if 'fetch_omdb' in request.form or 'fetch_omdb_flag' in request.form:
                # OMDb-API Call
                title = request.form['name']
                api_key = 'bfefad64'  # REAL API-KEY
                url = f'http://www.omdbapi.com/?t={title}&apikey={api_key}&type=movie&plot=short&r=json'
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('Response') == 'True':
                        omdb_data = {
                            'name': data.get('Title', ''),
                            'director': data.get('Director', ''),
                            'year': int(data.get('Year', 0)) if data.get('Year', '').isdigit() else '',
                            'rating': float(data.get('imdbRating', 0)) if data.get('imdbRating', '0').replace('.', '', 1).isdigit() else '',
                            'poster': data.get('Poster', '')
                        }
                    else:
                        error = 'Movie not found!'
                else:
                    error = 'Error with OMDb request.'
                return render_template('add_movie.html', user_id=user_id, omdb_data=omdb_data, error=error)
            else:
                # Validate year and rating fields
                year = request.form['year']
                rating = request.form['rating']
                if not year or not rating:
                    error = 'Year and rating fields must not be empty.'
                    return render_template('add_movie.html', user_id=user_id, omdb_data=omdb_data, error=error)
                try:
                    year = int(year)
                    rating = float(rating)
                except ValueError:
                    error = 'Year must be an integer and rating must be a number.'
                    return render_template('add_movie.html', user_id=user_id, omdb_data=omdb_data, error=error)
                movie = {
                    'name': request.form['name'],
                    'director': request.form['director'],
                    'year': year,
                    'rating': rating,
                    'user_id': user_id
                }
                data_manager.add_movie(movie)
                return redirect(url_for('user_movies', user_id=user_id))
    except Exception as ex:
        error = f'Error: {str(ex)}'
        return render_template('add_movie.html', user_id=user_id, omdb_data=omdb_data, error=error)
    return render_template('add_movie.html', user_id=user_id, omdb_data=omdb_data, error=error)

@app.route('/users/<int:user_id>/update_movie/<int:movie_id>', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    """
    Display a form to update a movie for a user and handle form submission.
    Args:
        user_id (int): The ID of the user.
        movie_id (int): The ID of the movie.
    """
    movies = data_manager.get_user_movies(user_id)
    movie = next((m for m in movies if m.id == movie_id), None)
    if not movie:
        return redirect(url_for('user_movies', user_id=user_id))
    if request.method == 'POST':
        updated_movie = {
            'id': movie_id,
            'name': request.form['name'],
            'director': request.form['director'],
            'year': int(request.form['year']),
            'rating': float(request.form['rating'])
        }
        data_manager.update_movie(updated_movie)
        return redirect(url_for('user_movies', user_id=user_id))
    return render_template('edit_movie.html', movie=movie)

@app.route('/users/<int:user_id>/delete_movie/<int:movie_id>')
def delete_movie(user_id, movie_id):
    """
    Delete a movie for a user and redirect to the user's movie list.
    Args:
        user_id (int): The ID of the user.
        movie_id (int): The ID of the movie.
    """
    data_manager.delete_movie(movie_id)
    return redirect(url_for('user_movies', user_id=user_id))

@app.route('/movies/<int:movie_id>/reviews', methods=['GET'])
def movie_reviews(movie_id):
    """
    Display all reviews for a specific movie.
    Args:
        movie_id (int): The ID of the movie.
    """
    reviews = data_manager.get_reviews_for_movie(movie_id)
    return render_template('reviews.html', reviews=reviews, movie_id=movie_id)

@app.route('/movies/<int:movie_id>/add_review', methods=['GET', 'POST'])
def add_review(movie_id):
    """
    Display a form to add a new review for a movie and handle form submission.
    Args:
        movie_id (int): The ID of the movie.
    """
    error = None
    if request.method == 'POST':
        try:
            user_id = int(request.form['user_id'])
            review_text = request.form['review_text']
            rating = float(request.form['rating'])
            data_manager.add_review({
                'user_id': user_id,
                'movie_id': movie_id,
                'review_text': review_text,
                'rating': rating
            })
            return redirect(url_for('movie_reviews', movie_id=movie_id))
        except Exception as ex:
            error = f'Error: {str(ex)}'
    users = data_manager.get_all_users()
    return render_template('add_review.html', movie_id=movie_id, users=users, error=error)

@app.errorhandler(404)
def page_not_found(e):
    """
    Render the 404 error page when a resource is not found.
    """
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050)
