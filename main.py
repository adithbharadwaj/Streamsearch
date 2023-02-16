import requests
from urllib.parse import urljoin

from flask import Flask, redirect, url_for, request, render_template

from helpers.tmdb import send_search_request
from helpers.parse import parse_search_results

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

@app.route('/select_movie', methods=['POST', 'GET'])
def select_movie():
    movie_id = request.args['id']
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/watch/providers?api_key={API_KEY}"
    data = requests.get(url).json()['results']
    if 'US' not in data:
        print('no US')
        return redirect('http://localhost:5000')

    data = data['US']
    rent, buy, subscribe = [], [], []

    if 'rent' in data:
        for key in data['rent']:
            rent.append(key['provider_name'])

    if 'buy' in data:
        for key in data['buy']:
            buy.append(key['provider_name'])

    if 'flatrate' in data:
        for key in data['flatrate']:
            subscribe.append(key['provider_name'])

    l = max(len(rent), len(buy), len(subscribe))
    res = [['NA' for i in range(3)] for j in range(l)]
    for i in range(l):
        if i < len(rent):
            res[i][0] = rent[i]
        if i < len(buy):
            res[i][1] = buy[i]
        if i < len(subscribe):
            res[i][2] = subscribe[i]

    return render_template('display_providers.html', result=res)

if __name__ == '__main__':
    app.secret_key = 'super secret key'

    app.debug = True
    app.run(host='0.0.0.0')
