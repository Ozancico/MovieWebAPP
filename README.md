# MovieWebAPP

MovieWebAPP ist eine moderne Webanwendung zur Verwaltung von Filmen, Nutzern und Bewertungen. Die App bietet eine intuitive Benutzeroberfläche und nutzt aktuelle Webtechnologien für ein ansprechendes Nutzererlebnis.

## Features
- **Benutzerverwaltung:** Nutzer können einfach hinzugefügt und verwaltet werden.
- **Filmliste:** Jeder Nutzer kann seine eigene Filmliste anlegen, bearbeiten und löschen.
- **Filmdetails & OMDb-Integration:** Neue Filme können manuell oder automatisch über die OMDb-API hinzugefügt werden. Die wichtigsten Filmdaten werden dabei automatisch übernommen.
- **Bewertungen:** Nutzer können Filme bewerten und Rezensionen verfassen. Alle Bewertungen sind übersichtlich einsehbar.
- **Responsives Design:** Die App ist für Desktop und mobile Geräte optimiert und verwendet ein modernes, ansprechendes CSS-Design.

## Technologie-Stack
- **Backend:** Python 3, Flask, SQLAlchemy (SQLite)
- **Frontend:** HTML5, CSS3 (modernes, responsives Design)
- **API:** OMDb API für Filmdaten

## Schnellstart
1. **Repository klonen:**
   ```bash
   git clone <repo-url>
   cd MovieWebAPP
   ```
2. **Abhängigkeiten installieren:**
   ```bash
   pip install -r requirements.txt
   ```
3. **App starten:**
   ```bash
   python app.py
   ```
4. **Im Browser öffnen:**
   [http://localhost:5000](http://localhost:5000)

## Projektstruktur
- `app.py` – Hauptanwendung (Flask)
- `datamanager/` – Datenzugriffsschicht (SQLAlchemy)
- `templates/` – HTML-Templates (Jinja2)
- `static/` – Statische Dateien (CSS)

## Screenshots
*Füge hier Screenshots deiner App ein, um das Design und die Funktionen zu zeigen.*

## Lizenz
MIT License

---
**MovieWebAPP** – Dein moderner Begleiter für Filmverwaltung und Bewertungen!
