from flask_login import LoginManager

from routes import app
from helpers.user import User, db

db.init_app(app)

with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.query.get(int(user_id))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, ssl_context='adhoc')
