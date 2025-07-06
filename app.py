from flask import Flask, render_template, request, redirect, url_for, session
from datamanager.sqlite_data_manager import SQLiteDataManager
import requests
import os
import math
import json
from dotenv import load_dotenv

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
    with open('trending_titles.json', 'r') as f:
        trending_titles = json.load(f)
    per_page = 24
    total_pages = math.ceil(len(trending_titles) / per_page)
    start = (page - 1) * per_page
    end = start + per_page
    page_titles = trending_titles[start:end]
    omdb_movies = []
    # Prüfe, ob der Film bereits in der DB ist, sonst OMDb-API
    for title in page_titles:
        # Suche nach Film in der DB (global, nicht nach User gefiltert)
        db_movie = None
        # Hole alle Filme und suche nach exaktem Titel
        all_movies = data_manager.get_all_movies()
        for m in all_movies:
            if m.name.lower() == title.lower():
                db_movie = m
                break
        if db_movie and db_movie.omdb_poster:
            omdb_movies.append({
                'name': db_movie.name,
                'director': db_movie.omdb_director or db_movie.director,
                'year': db_movie.omdb_year or db_movie.year,
                'rating': db_movie.omdb_rating or db_movie.rating,
                'poster': db_movie.omdb_poster,
                'omdb_id': None
            })
        else:
            OMDB_API_KEY = os.getenv('OMDB_API_KEY')
            url = (f'http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}'
                   f'&type=movie&plot=short&r=json')
            try:
                r = requests.get(url)
                if r.status_code == 200:
                    data = r.json()
                    if data.get('Response') == 'True':
                        omdb_movies.append({
                            'name': data.get('Title', ''),
                            'director': data.get('Director', ''),
                            'year': data.get('Year', ''),
                            'rating': data.get('imdbRating', ''),
                            'poster': data.get('Poster', ''),
                            'omdb_id': data.get('imdbID', '')
                        })
            except Exception:
                pass
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
    return render_template('users.html', users=users)


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
    return render_template(
        'movies.html',
        movies=movies_with_omdb,
        user_id=user_id)


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    """
    Display a form to add a new user and handle form submission.
    """
    if request.method == 'POST':
        name = request.form['name']
        user = data_manager.add_user({'name': name})
        if user is None:
            error = f"User '{name}' existiert bereits. Bitte wähle einen anderen Namen."
            back_url = request.args.get('back') or session.get(
                'last_url') or url_for('list_users')
            return render_template(
                'add_user.html',
                back_url=back_url,
                error=error)
        back_url = request.args.get('back') or session.get(
            'last_url') or url_for('list_users')
        return redirect(back_url)
    back_url = request.args.get('back') or session.get(
        'last_url') or url_for('list_users')
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
    back_url = request.args.get('back') or session.get(
        'last_url') or url_for('user_movies', user_id=user_id)
    try:
        if request.method == 'POST':
            if 'fetch_omdb' in request.form or 'fetch_omdb_flag' in request.form:
                title = request.form['name']
                api_key = os.getenv('OMDB_API_KEY')
                url = f'http://www.omdbapi.com/?t={title}&apikey={api_key}&type=movie&plot=short&r=json'
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('Response') == 'True':
                        omdb_data = {
                            'name': data.get(
                                'Title',
                                ''),
                            'director': data.get(
                                'Director',
                                ''),
                            'year': int(
                                data.get(
                                    'Year',
                                    0)) if data.get(
                                'Year',
                                '').isdigit() else '',
                            'rating': float(
                                data.get(
                                    'imdbRating',
                                    0)) if data.get(
                                    'imdbRating',
                                    '0').replace(
                                        '.',
                                        '',
                                        1).isdigit() else '',
                            'poster': data.get(
                                            'Poster',
                                '')}
                    else:
                        error = 'Movie not found!'
                else:
                    error = 'Error with OMDb request.'
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
                        error = f'Das Jahr muss zwischen 1888 und {current_year} liegen.'
                        return render_template(
                            'add_movie.html',
                            user_id=user_id,
                            omdb_data=omdb_data,
                            error=error,
                            back_url=back_url)
                    if not (0.0 <= rating <= 10.0):
                        error = 'Die Bewertung muss zwischen 0 und 10 liegen.'
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
                    error = f"Der Film '{
                        movie['name']}' ({year}) ist für diesen Nutzer bereits vorhanden."
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
    back_url = request.args.get('back') or session.get(
        'last_url') or url_for('user_movies', user_id=user_id)
    if not movie:
        return redirect(url_for('user_movies', user_id=user_id))
    poster_url = None
    OMDB_API_KEY = os.getenv('OMDB_API_KEY')
    if movie and movie.name:
        url = f'http://www.omdbapi.com/?t={
            movie.name}&apikey={OMDB_API_KEY}&type=movie&plot=short&r=json'
        try:
            r = requests.get(url)
            if r.status_code == 200:
                data = r.json()
                if data.get('Response') == 'True':
                    poster_url = data.get('Poster', None)
        except Exception:
            pass
    if request.method == 'POST':
        try:
            year = int(request.form['year'])
            rating = float(request.form['rating'])
            current_year = 2025  # oder: datetime.now().year
            if not (1888 <= year <= current_year):
                error = f'Das Jahr muss zwischen 1888 und {current_year} liegen.'
                movie_dict = movie.__dict__ if hasattr(
                    movie, '__dict__') else dict(movie)
                movie_dict['poster'] = poster_url
                return render_template(
                    'edit_movie.html',
                    movie=movie_dict,
                    back_url=back_url,
                    error=error)
            if not (0.0 <= rating <= 10.0):
                error = 'Die Bewertung muss zwischen 0 und 10 liegen.'
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
    return render_template('reviews.html', reviews=reviews, movie_id=movie_id)


@app.route('/movies/<int:movie_id>/add_review', methods=['GET', 'POST'])
def add_review(movie_id):
    """
    Display a form to add a new review for a movie and handle form submission.
    Args:
        movie_id (int): The ID of the movie.
    """
    error = None
    back_url = request.args.get('back') or session.get(
        'last_url') or url_for('movie_reviews', movie_id=movie_id)
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
            # Optional: OMDb-API abfragen, wenn keine lokalen Treffer
            OMDB_API_KEY = os.getenv('OMDB_API_KEY')
            url = f'http://www.omdbapi.com/?t={query}&apikey={OMDB_API_KEY}&type=movie&plot=short&r=json'
            try:
                r = requests.get(url)
                if r.status_code == 200:
                    data = r.json()
                    if data.get('Response') == 'True':
                        omdb_result = {
                            'name': data.get('Title', ''),
                            'director': data.get('Director', ''),
                            'year': data.get('Year', ''),
                            'rating': data.get('imdbRating', ''),
                            'poster': data.get('Poster', ''),
                            'omdb_id': data.get('imdbID', '')
                        }
            except Exception:
                pass
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
