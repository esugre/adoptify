from flask import Flask

app = Flask(__name__)

from app import routes

# Vorbereitung für Sessions
app.secret_key = 'geheimigeheimenstein'