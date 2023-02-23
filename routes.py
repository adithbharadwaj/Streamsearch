from flask import Flask, redirect, url_for, request, render_template, session, flash
import pycountry
from flask_login import login_user, login_required, logout_user, current_user

from helpers.tmdb import send_search_request, send_metadata_request
from helpers.parse import filter_on_region, parse_search_results, extract_providers, MediaType, ALL_LOCALES, get_watchlist

from werkzeug.security import generate_password_hash, check_password_hash
from users.user import User, Movies

app = Flask(__name__)
app.secret_key = 'secret'
app.debug = True


@app.route('/')
def login():
    return render_template('login.html')


@app.route('/main')
@login_required
def main():
    return render_template('main.html', all_locales=ALL_LOCALES)


@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/show-watchlist')
@login_required
def show_watchlist():
    user_id = current_user.get_id()
    watch_list = get_watchlist(user_id)
    return render_template('watchlist.html', watchlist=watch_list)

@app.route('/signup', methods=['POST'])
def signup_post():
    # code to validate and add user to database goes here
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    user = User.query.filter_by(
        email=email).first()  # if this returns a user, then the email already exists in database

    if user:  # if a user is found, we want to redirect back to signup page so user can try again
        return render_template('signup.html', msg='email already exists. please try a different email')

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))
    new_user.add_to_db()

    return redirect(url_for('login'))


@app.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return render_template('login.html',
                               msg='Error: user does not exist')  # if the user doesn't exist or password is wrong, reload the page

    login_user(user, remember=remember)

    return redirect(url_for('main'))


@app.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == 'POST':
        locale = pycountry.countries.get(alpha_2=request.form['locale'])
        query = request.form['search']
        results = send_search_request(query, locale.alpha_2)['results']
        session['locale'] = locale.alpha_2
        medias = parse_search_results(results)
        medias = filter_on_region(medias, locale.alpha_2)
        if medias:
            return render_template('movies_list.html', medias=medias, all_locales=ALL_LOCALES)
        else:
            return render_template('movies_not_found.html')
    else:
        return render_template('movies_list.html', all_locales=ALL_LOCALES)

@app.route('/providers', methods=['POST', 'GET'])
def select_movie():
    locale_code = None
    if 'locale' in session:
        locale_code = session['locale']
    media_id, media_title, media_type = request.args['id'], request.args['title'], MediaType(request.args['media_type'])
    results = send_metadata_request(media_id, media_type)['results']
    providers = extract_providers(results, locale_code)

    return render_template('providers.html', providers=providers, title=media_title)


@app.route('/watchlist')
@login_required
def watchlist():
    movie_id = request.args['id']
    movie_name = request.args['title']
    media_path = request.args['path']

    user_id = current_user.get_id()

    movie = Movies(user_id=user_id, movie_id=movie_id, movie_name=movie_name, path=media_path)

    mov = Movies.query.filter_by(movie_id=movie_id, user_id=user_id).first()
    if not mov:
        movie.add_to_db()

    watch_list = get_watchlist(user_id)

    return render_template('watchlist.html', watchlist=watch_list)

