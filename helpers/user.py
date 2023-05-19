from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    movies = db.relationship('Movies', lazy=True, backref='user')

    def add_to_db(self):
        db.session.add(self)
        db.session.commit()

class Movies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    movie_id = db.Column(db.Integer)
    movie_name = db.Column(db.String(1000))
    path = db.Column(db.String())

    def add_to_db(self):
        db.session.add(self)
        db.session.commit()
