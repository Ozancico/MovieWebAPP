# MovieWebAPP

MovieWebAPP is a modern web application for managing movies, users, and reviews. The app offers an intuitive user interface and leverages up-to-date web technologies for an appealing user experience.

## Features
- **User Management:** Easily add and manage users.
- **Movie List:** Each user can create, edit, and delete their own movie list.
- **Movie Details & OMDb Integration:** Add new movies manually or automatically via the OMDb API. Key movie data is fetched automatically.
- **Reviews:** Users can rate movies and write reviews. All reviews are clearly displayed.
- **Responsive Design:** The app is optimized for desktop and mobile devices and uses a modern, attractive CSS design.

## Technology Stack
- **Backend:** Python 3, Flask, SQLAlchemy (SQLite)
- **Frontend:** HTML5, CSS3 (modern, responsive design)
- **API:** OMDb API for movie data

## Quickstart
1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd MovieWebAPP
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Start the app:**
   ```bash
   python app.py
   ```
4. **Open in your browser:**
   [http://localhost:5000](http://localhost:5000)

## Project Structure
- `app.py` – Main application (Flask)
- `datamanager/` – Data access layer (SQLAlchemy)
- `templates/` – HTML templates (Jinja2)
- `static/` – Static files (CSS)

## Screenshots
*Add screenshots of your app here to showcase the design and features.*

## License
MIT License

---
**MovieWebAPP** – Your modern companion for movie management and reviews!
