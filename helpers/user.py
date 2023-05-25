from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

from helpers.model import MediaType
from helpers.tmdb import fetch_media

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    watchlist = db.relationship('UserMedia', lazy=True, backref='user')

    def add_to_db(self):
        db.session.add(self)
        db.session.commit()

class UserMedia(db.Model):
    dummy_id = db.Column(db.Integer, autoincrement=True, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # `media_id` and `media_type` together uniquely identify a `model.Media`.
    media_id = db.Column(db.Integer)
    media_type = db.Column(db.String(5))

    def add_to_db(self):
        db.session.add(self)
        db.session.commit()

def get_watchlist(user_id):
    user = User.query.filter_by(id=user_id).first()
    watchlist = []

    for user_media in user.watchlist:
        watchlist.append(fetch_media(user_media.media_id, MediaType.MOVIE))

    return watchlist
