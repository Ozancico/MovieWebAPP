"""
Utility functions for the MovieWebAPP.
"""
import os
import requests
from typing import Optional, Dict, Any


def fetch_omdb_data(title: str) -> Optional[Dict[str, Any]]:
    """
    Fetch movie data from OMDb API.
    
    Args:
        title (str): Movie title to search for
        
    Returns:
        Optional[Dict[str, Any]]: Movie data or None if not found
    """
    api_key = os.getenv('OMDB_API_KEY')
    if not api_key:
        return None
        
    url = f'http://www.omdbapi.com/?t={title}&apikey={api_key}&type=movie&plot=short&r=json'
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data.get('Response') == 'True':
                return {
                    'name': data.get('Title', ''),
                    'director': data.get('Director', ''),
                    'year': int(data.get('Year', 0)) if data.get('Year', '').isdigit() else '',
                    'rating': float(data.get('imdbRating', 0)) if data.get('imdbRating', '0').replace('.', '', 1).isdigit() else '',
                    'poster': data.get('Poster', ''),
                    'omdb_id': data.get('imdbID', '')
                }
    except Exception:
        pass
    
    return None


def validate_movie_data(year: int, rating: float) -> tuple[bool, str]:
    """
    Validate movie year and rating.
    
    Args:
        year (int): Movie year
        rating (float): Movie rating
        
    Returns:
        tuple[bool, str]: (is_valid, error_message)
    """
    current_year = 2025  # or: datetime.now().year
    
    if not (1888 <= year <= current_year):
        return False, f'The year must be between 1888 and {current_year}.'
    
    if not (0.0 <= rating <= 10.0):
        return False, 'The rating must be between 0 and 10.'
    
    return True, ""


def get_back_url(request, session, default_url: str) -> str:
    """
    Get the back URL from request parameters or session.
    
    Args:
        request: Flask request object
        session: Flask session object
        default_url (str): Default URL if no back URL is found
        
    Returns:
        str: Back URL
    """
    return request.args.get('back') or session.get('last_url') or default_url 