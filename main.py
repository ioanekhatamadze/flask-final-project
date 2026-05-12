from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(_name_)

db = SQLAlchemy(app)