# app.py
from flask import Flask
from datamanager.sqlite_data_manager import SQLiteDataManager

app = Flask(__name__)
db_manager = SQLiteDataManager("moviweb.db")

@app.route('/')
def home():
    return "Welcome to MovieWeb App!"

if __name__ == '__main__':
    app.run(debug=True)
