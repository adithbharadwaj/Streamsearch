import requests
from urllib.parse import urljoin

from flask import Flask, redirect, url_for, request, render_template

from helpers.tmdb import send_search_request, send_metadata_request
from helpers.parse import parse_search_results, extract_providers, MediaType

app = Flask(__name__)

@app.route('/')
def main():
    return render_template('search.html')

@app.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == 'POST':
        query = request.form['search']
        results = send_search_request(query)['results']
        medias = parse_search_results(results)

        return render_template('search.html', medias=medias)

@app.route('/providers', methods=['POST', 'GET'])
def select_movie():
    media_id, media_title, media_type = request.args['id'], request.args['title'], MediaType(request.args['media_type'])
    results = send_metadata_request(media_id, media_type)['results']
    providers = extract_providers(results, 'US')

    return render_template('providers.html', providers=providers, title=media_title)

if __name__ == '__main__':
    app.secret_key = 'super secret key'

    app.debug = True
    app.run(host='0.0.0.0')
