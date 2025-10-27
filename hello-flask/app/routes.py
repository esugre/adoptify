
from app import app

@app.route('/')
def index():
    return "Frischer Fisch!"