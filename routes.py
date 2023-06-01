import json
import os
import uuid

import requests
from flask import (Flask, flash, jsonify, redirect, render_template, request,
                   session, url_for)
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from helpers.locale import coordsToLocale, ipToLocale
from helpers.model import ALL_LOCALES, MediaType
from helpers.oauth import (GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, client,
                           get_google_provider_cfg)
from helpers.recommender import load_similarity, topn_similar
from helpers.send_email import send_email, start_threads
from helpers.tmdb import (fetch_media, fetch_providers, fetch_search_results,
                          ungroup_providers, generate_genre_list, generate_genre_map, filter_on_genre)
                          ungroup_providers, get_trailer)
from helpers.user import User, UserMedia, get_watchlist, Settings

app = Flask(__name__)
app.secret_key = 'secret'
app.debug = True

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

# load once
GENRE_MAP = generate_genre_map()

@app.route('/', methods=['POST', 'GET'])
def login():
    return render_template('login.html')

@app.route('/main', methods=['POST', 'GET'])
@login_required
def main():
    if request.method == 'POST':
        # Auto-determining locale.
        coords = json.loads(request.data.decode('utf-8'))
        if coords != {}:
            app.logger.debug(f'Used coordinates {coords} to determine locale.')
            session['locale'] = coordsToLocale([coords['lat'], coords['long']])
        else:
            client_ip = request.remote_addr     # IMP: Will not work if using proxy. Change if required.
            app.logger.debug(f'Used client IP {client_ip} to determine locale.')
            session['locale'] = ipToLocale(client_ip)
        return jsonify(session['locale'])
    else:
        return render_template('main.html', all_locales=ALL_LOCALES, genres=generate_genre_list())

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
    watchlist = get_watchlist(user_id)
    return render_template('watchlist.html', watchlist=watchlist, user_id=user_id)

@app.route('/show-watchlist/<int:user_id>')
def show_watchlist_userid(user_id):
    watchlist = get_watchlist(user_id)
    return render_template('watchlist.html', watchlist=watchlist)

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

    user_id = int(str(uuid.uuid1().int)[:16])
    print("uuid id: ", user_id)
    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = User(id=user_id, email=email, name=name, password=generate_password_hash(password, method='sha256'))
    new_user.add_to_db()

    return redirect(url_for('login'))

@app.route('/login_oauth')
def login_oauth():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri="{0}/callback".format(request.base_url),
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@app.route("/login_oauth/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # You want to make sure their email is verified.
    # The user authenticated with Google, authorized your
    # app, and now you've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    user = User(
        id=unique_id, name=users_name, email=users_email
    )

    # Doesn't exist? Add it to the database.
    exists = User.query.filter_by(email=users_email).first()
    if not exists:
        user.add_to_db()

    # Begin user session by logging the user in
    login_user(user)

    # Send user back to homepage
    return redirect(url_for("main"))

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
        if not user:
            msg = 'User does not exist. Please sign up.'
        else:
            msg = f'Wrong password, try again.'
        return render_template('login.html', msg=msg)  # if the user doesn't exist or password is wrong, reload the page

    login_user(user, remember=remember)

    return redirect(url_for('main'))

@app.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == 'POST':
        query = request.form.get('search')
        medias = fetch_search_results(query, session['locale'])
        medias = filter_on_genre(medias, request.form.get('genre'), GENRE_MAP)
        # medias = filter_on_region(medias, session['locale'])

        if medias:
            return render_template('search-success.html', medias=medias, all_locales=ALL_LOCALES)
        else:
            return render_template('search-failure.html')

    else:
        return render_template('search-success.html', all_locales=ALL_LOCALES)

# Load once
SIMILARITY_MOVIE = load_similarity(os.path.join('static', 'recommender', 'similarity-5000.pkl'))
SIMILARITY_TV = None

@app.route('/providers', methods=['POST', 'GET'])
def select_media():
    locale_code = None
    if 'locale' in session:
        locale_code = session['locale']

    media_id, media_title, media_type = request.args['id'], request.args['title'], MediaType(request.args['media_type'])
    media = fetch_media(media_id, media_type)

    providers = fetch_providers(media.id, media.media_type, locale_code)
    providers = ungroup_providers(providers)

    trailer = get_trailer(media_id)

    if media.media_type == MediaType.MOVIE:
        similar_ids = topn_similar(SIMILARITY_MOVIE, media.id, n=10)
        recs = [fetch_media(similar_id, media.media_type) for similar_id in similar_ids]
    elif media.media_type == MediaType.TV:
        # TODO
        recs = []

    return render_template('providers.html', providers=providers, media=media, recs=recs, trailer=trailer)

@app.route('/watchlist')
@login_required
def watchlist():
    media_id = request.args['media_id']
    media_type = request.args['media_type']

    user_id = current_user.get_id()

    user_media = UserMedia(user_id=user_id, media_id=media_id, media_type=media_type)

    found = UserMedia.query.filter_by(user_id=user_id, media_id=media_id, media_type=media_type).first()
    if not found:
        user_media.add_to_db()

    watch_list = get_watchlist(user_id)

    return render_template('watchlist.html', watchlist=watch_list, user_id=user_id)

@app.route('/send_email', methods=['POST'])
@login_required
def email():
    user_id = current_user.get_id()
    query = int(request.form.get('settings'))
    watch_list = get_watchlist(user_id)

    medias = [fetch_media(movies.title, MediaType.MOVIE) for movies in watch_list]

    recs = []
    for media in medias:
        if media.media_type == MediaType.MOVIE:
            similar_ids = topn_similar(SIMILARITY_MOVIE, media.id, n=10)
            for similar_id in similar_ids:
                recs.append(fetch_media(similar_id, media.media_type))

    user = User.query.filter_by(id=user_id).first()
    setting = Settings(user_id=user_id, frequency=query, email=user.email)
    setting.add_to_db()

    freq = Settings.query.filter_by(frequency=1).all()
    res = []
    for frequency in freq:
        res.append(frequency)

    start_threads(res)

    return render_template('watchlist.html', watchlist=watch_list)
