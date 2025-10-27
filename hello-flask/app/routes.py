
from app import app

@app.route('/')
def index():
    return "Hallo, Welt!"