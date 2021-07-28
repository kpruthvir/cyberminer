from flask import Flask
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = 'secret_key'

from cyberminer_app import search, users, clean