from flask import Flask, redirect, url_for, request, render_template, session
import pycountry

from helpers.tmdb import send_search_request, send_metadata_request
from helpers.parse import filter_on_region, parse_search_results, extract_providers, MediaType, ALL_LOCALES

app = Flask(__name__)

@app.route('/')
def main():
    return render_template('main.html', all_locales=ALL_LOCALES)

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
    locale_code = 'US'
    if 'locale' in session:
        locale_code = session['locale']
    media_id, media_title, media_type = request.args['id'], request.args['title'], MediaType(request.args['media_type'])
    results = send_metadata_request(media_id, media_type)['results']
    providers = extract_providers(results, locale_code)

    return render_template('providers.html', providers=providers, title=media_title)

