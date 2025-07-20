from flask import Flask, render_template, request, redirect, url_for, session
from MovieWebAPP.datamanager.sqlite_data_manager import SQLiteDataManager
import requests
import os
import math
import json
from dotenv import load_dotenv
from MovieWebAPP.utils import fetch_omdb_data, validate_movie_data, get_back_url, load_trending_titles

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')
data_manager = SQLiteDataManager('moviwebapp.db')
load_dotenv()


@app.before_request
def store_referrer():
    """
    Store the previous page in the session, except for static files and POST
    requests.
    """
    if request.method == 'GET' and not request.path.startswith('/static'):
        session['last_url'] = request.referrer if request.referrer else url_for(
            'home')


@app.route('/')
def home():
    """
    Show the homepage with OMDb top-rated/trending movies (10 per page,
    pagination, 10 pages).
    """
    page = int(request.args.get('page', 1))
    users = data_manager.get_all_users()
    # Initialisiere Trending-Titel in der DB, falls noch keine Filme vorhanden sind
    all_movies = data_manager.get_all_movies()
    if not all_movies:
        try:
            trending_titles = load_trending_titles()
            for title in trending_titles:
                # Prüfe, ob der Film schon existiert (global, user_id=0)
                exists = any(m.name.lower() == title.lower() for m in all_movies)
                if not exists:
                    data = fetch_omdb_data(title)
                    if data:
                        movie = {
                            'name': data['name'],
                            'director': data['director'],
                            'year': data['year'],
                            'rating': data['rating'],
                            'user_id': 0  # globaler User für Trending-Titel
                        }
                        data_manager.add_movie(movie)
            all_movies = data_manager.get_all_movies()
        except Exception as e:
            print(f"Error initializing trending titles: {e}")
    per_page = 24
    total_pages = math.ceil(len(all_movies) / per_page) if all_movies else 1
    start = (page - 1) * per_page
    end = start + per_page
    page_movies = all_movies[start:end]
    omdb_movies = []
    for m in page_movies:
        omdb_movies.append({
            'name': m.name,
            'director': m.omdb_director or m.director,
            'year': m.omdb_year or m.year,
            'rating': m.omdb_rating or m.rating,
            'poster': m.omdb_poster,
            'omdb_id': None
        })
    return render_template(
        'home.html',
        omdb_movies=omdb_movies,
        users=users,
        page=page,
        total_pages=total_pages)


@app.route('/users')
def list_users():
    """
    Display a list of all users.
    """
    users = data_manager.get_all_users()
    back_url = get_back_url(request, session, url_for('list_users'))
    return render_template('users.html', users=users, back_url=back_url)


@app.route('/users/<int:user_id>')
def user_movies(user_id):
    """
    Show the movie list of a user with OMDb info (poster, etc.) as on the homepage.
    """
    movies = data_manager.get_user_movies(user_id)
    movies_with_omdb = []
    for movie in movies:
        movies_with_omdb.append({
            'id': movie.id,
            'name': movie.name,
            'director': movie.omdb_director or movie.director,
            'year': movie.omdb_year or movie.year,
            'rating': movie.omdb_rating or movie.rating,
            'poster': movie.omdb_poster,
        })
    back_url = get_back_url(request, session, url_for('user_movies', user_id=user_id))
    return render_template(
        'movies.html',
        movies=movies_with_omdb,
        user_id=user_id,
        back_url=back_url)


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    """
    Display a form to add a new user and handle form submission.
    """
    if request.method == 'POST':
        name = request.form['name']
        user = data_manager.add_user({'name': name})
        if user is None:
            error = f"User '{name}' already exists. Please choose another name."
            back_url = get_back_url(request, session, url_for('list_users'))
            return render_template(
                'add_user.html',
                back_url=back_url,
                error=error)
        back_url = get_back_url(request, session, url_for('list_users'))
        return redirect(back_url)
    back_url = get_back_url(request, session, url_for('list_users'))
    return render_template('add_user.html', back_url=back_url)


@app.route('/users/<int:user_id>/add_movie', methods=['GET', 'POST'])
def add_movie(user_id):
    """
    Display a form to add a new movie for a user, handle OMDb API lookup and form submission.
    Args:
        user_id (int): The ID of the user.
    """
    omdb_data = None
    error = None
    back_url = get_back_url(request, session, url_for('user_movies', user_id=user_id))
    try:
        if request.method == 'POST':
            if 'fetch_omdb' in request.form or 'fetch_omdb_flag' in request.form:
                title = request.form['name']
                data = fetch_omdb_data(title)
                if data:
                    omdb_data = data
                else:
                    error = 'Movie not found!'
                return render_template(
                    'add_movie.html',
                    user_id=user_id,
                    omdb_data=omdb_data,
                    error=error,
                    back_url=back_url)
            else:
                year = request.form['year']
                rating = request.form['rating']
                if not year or not rating:
                    error = 'Year and rating fields must not be empty.'
                    return render_template(
                        'add_movie.html',
                        user_id=user_id,
                        omdb_data=omdb_data,
                        error=error,
                        back_url=back_url)
                try:
                    year = int(year)
                    rating = float(rating)
                    current_year = 2025  # oder: datetime.now().year
                    if not (1888 <= year <= current_year):
                        error = f'The year must be between 1888 and {current_year}.'
                        return render_template(
                            'add_movie.html',
                            user_id=user_id,
                            omdb_data=omdb_data,
                            error=error,
                            back_url=back_url)
                    if not (0.0 <= rating <= 10.0):
                        error = 'The rating must be between 0 and 10.'
                        return render_template(
                            'add_movie.html',
                            user_id=user_id,
                            omdb_data=omdb_data,
                            error=error,
                            back_url=back_url)
                except ValueError:
                    error = 'Year must be an integer and rating must be a number.'
                    return render_template(
                        'add_movie.html',
                        user_id=user_id,
                        omdb_data=omdb_data,
                        error=error,
                        back_url=back_url)
                movie = {
                    'name': request.form['name'],
                    'director': request.form['director'],
                    'year': year,
                    'rating': rating,
                    'user_id': user_id
                }
                result = data_manager.add_movie(movie)
                if result is None:
                    error = f"The film '{movie['name']}' ({year}) is already present for this user."
                    return render_template(
                        'add_movie.html',
                        user_id=user_id,
                        omdb_data=omdb_data,
                        error=error,
                        back_url=back_url)
                return redirect(url_for('user_movies', user_id=user_id))
    except Exception as ex:
        error = f'Error: {str(ex)}'
        return render_template(
            'add_movie.html',
            user_id=user_id,
            omdb_data=omdb_data,
            error=error,
            back_url=back_url)
    return render_template(
        'add_movie.html',
        user_id=user_id,
        omdb_data=omdb_data,
        error=error,
        back_url=back_url)


@app.route('/users/<int:user_id>/update_movie/<int:movie_id>',
           methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    """
    Display a form to update a movie for a user and handle form submission.
    Args:
        user_id (int): The ID of the user.
        movie_id (int): The ID of the movie.
    """
    movies = data_manager.get_user_movies(user_id)
    movie = next((m for m in movies if m.id == movie_id), None)
    back_url = get_back_url(request, session, url_for('user_movies', user_id=user_id))
    if not movie:
        return redirect(url_for('user_movies', user_id=user_id))
    poster_url = None
    if movie and movie.name:
        data = fetch_omdb_data(movie.name)
        if data:
            poster_url = data.get('poster', None)
    if request.method == 'POST':
        try:
            year = int(request.form['year'])
            rating = float(request.form['rating'])
            current_year = 2025  # oder: datetime.now().year
            if not (1888 <= year <= current_year):
                error = f'The year must be between 1888 and {current_year}.'
                movie_dict = movie.__dict__ if hasattr(
                    movie, '__dict__') else dict(movie)
                movie_dict['poster'] = poster_url
                return render_template(
                    'edit_movie.html',
                    movie=movie_dict,
                    back_url=back_url,
                    error=error)
            if not (0.0 <= rating <= 10.0):
                error = 'The rating must be between 0 and 10.'
                movie_dict = movie.__dict__ if hasattr(
                    movie, '__dict__') else dict(movie)
                movie_dict['poster'] = poster_url
                return render_template(
                    'edit_movie.html',
                    movie=movie_dict,
                    back_url=back_url,
                    error=error)
        except ValueError:
            error = 'Year must be an integer and rating must be a number.'
            movie_dict = movie.__dict__ if hasattr(
                movie, '__dict__') else dict(movie)
            movie_dict['poster'] = poster_url
            return render_template(
                'edit_movie.html',
                movie=movie_dict,
                back_url=back_url,
                error=error)
        updated_movie = {
            'id': movie_id,
            'name': request.form['name'],
            'director': request.form['director'],
            'year': year,
            'rating': rating
        }
        data_manager.update_movie(updated_movie)
        return redirect(url_for('user_movies', user_id=user_id))
    movie_dict = movie.__dict__ if hasattr(movie, '__dict__') else dict(movie)
    movie_dict['poster'] = poster_url
    return render_template(
        'edit_movie.html',
        movie=movie_dict,
        back_url=back_url)


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
    all_movies = data_manager.get_all_movies()
    movie = next((m for m in all_movies if m.id == movie_id), None)
    user_id = movie.user_id if movie else 1
    back_url = get_back_url(request, session, url_for('movie_reviews', movie_id=movie_id))
    return render_template('reviews.html', reviews=reviews, movie_id=movie_id, user_id=user_id, back_url=back_url)


@app.route('/movies/<int:movie_id>/add_review', methods=['GET', 'POST'])
def add_review(movie_id):
    """
    Display a form to add a new review for a movie and handle form submission.
    Args:
        movie_id (int): The ID of the movie.
    """
    error = None
    back_url = get_back_url(request, session, url_for('movie_reviews', movie_id=movie_id))
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
    return render_template(
        'add_review.html',
        movie_id=movie_id,
        users=users,
        error=error,
        back_url=back_url)


@app.route('/autocomplete_movie_title')
def autocomplete_movie_title():
    """
    Return a list of up to 10 movie titles and posters from OMDb that match the query (for autocomplete).
    Query param: q (the search string)
    Returns: JSON list of dicts with 'title' and 'poster'
    """
    import json
    OMDB_API_KEY = os.getenv('OMDB_API_KEY')
    query = request.args.get('q', '').strip()
    results = []
    if query and len(query) > 0:
        url = f'http://www.omdbapi.com/?s={query}&apikey={OMDB_API_KEY}&type=movie'
        try:
            r = requests.get(url)
            if r.status_code == 200:
                data = r.json()
                if data.get('Response') == 'True' and 'Search' in data:
                    for movie in data['Search'][:10]:
                        title = movie.get('Title', '')
                        poster = movie.get('Poster', '')
                        results.append({'title': title, 'poster': poster})
        except Exception:
            pass
    return json.dumps(results)


@app.route('/search')
def search():
    """
    Suche nach Filmen in der Datenbank (Titel, Regisseur, Jahr). Falls keine Treffer, optional OMDb.
    """
    query = request.args.get('q', '').strip()
    results = []
    omdb_result = None
    if query:
        results = data_manager.search_movies(query)
        if not results:
            data = fetch_omdb_data(query)
            if data:
                omdb_result = data
    return render_template(
        'search_results.html',
        query=query,
        results=results,
        omdb_result=omdb_result)


@app.errorhandler(404)
def page_not_found(e):
    """
    Render the 404 error page when a resource is not found.
    """
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050)
