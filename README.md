# MovieWebAPP

MovieWebAPP is a modern web application for managing movies, users, and reviews. The app offers an intuitive user interface and leverages up-to-date web technologies for an appealing user experience.

## Features
- **User Management:** Easily add and manage users (unique usernames enforced).
- **Movie List:** Each user can create, edit, and delete their own movie list. Duplicate movies for a user are prevented.
- **Movie Details & OMDb Integration:** Add new movies manually or automatically via the OMDb API. Key movie data is fetched and stored in the database to minimize API calls.
- **Reviews:** Users can rate movies and write reviews. All reviews are clearly displayed.
- **Search & Autocomplete:** Search for movies by title, director, or year. Autocomplete suggestions from OMDb API are shown as you type (case-insensitive, with poster images).
- **Error Handling & Validation:** Robust input validation and error handling for all database operations.
- **Responsive Design:** The app is optimized for desktop and mobile devices and uses a modern, attractive CSS design.

## Technology Stack
- **Backend:** Python 3, Flask, SQLAlchemy (SQLite)
- **Frontend:** HTML5, CSS3 (modern, responsive design)
- **API:** OMDb API for movie data

## Quickstart
1. **Clone the repository:**
   ```bash
   git clone https://github.com/Ozancico/MovieWebAPP.git
   cd MovieWebAPP
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure environment variables:**
   - A `.env` file is already included in the project root
   - Update the `.env` file with your OMDb API key:
   ```env
   OMDB_API_KEY=your_omdb_api_key_here
   FLASK_SECRET_KEY=your_secret_key_here
   ```
   You can get a free OMDb API key at https://www.omdbapi.com/apikey.aspx
4. **Start the app:**
   ```bash
   python app.py
   ```
5. **Open in your browser:**
   [http://localhost:5050](http://localhost:5050)

## Project Structure
- `app.py` – Main application (Flask)
- `datamanager/` – Data access layer (SQLAlchemy, models, interface)
- `templates/` – HTML templates (Jinja2)
- `static/` – Static files (CSS)
- `trending_titles.json` – List of trending movie titles for the homepage

## Best Practices & Notes
- **Unique Constraints:** Usernames are unique. Movies are unique per user (by name and year).
- **OMDb Data:** OMDb data is fetched and stored in the database to reduce API calls and improve performance.
- **Input Validation:** All user input is validated both client- and server-side.
- **Error Handling:** All database operations are wrapped in try/except blocks for robustness.
- **Search & Autocomplete:** Use the search bar on the homepage or search page. Autocomplete suggestions appear as you type (case-insensitive, with posters).
- **Language:** The entire app and all messages are in English.

## Screenshots
*Add screenshots of your app here to showcase the design and features.*

## License
MIT License

---
**MovieWebAPP** – Your modern companion for movie management and reviews!
