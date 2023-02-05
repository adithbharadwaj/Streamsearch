from flask import Flask, redirect, url_for, request, render_template
import requests

app = Flask(__name__)

'''
---------------------------------------------------------------------------------------------
routing to Display the Pages
'''
# initial page. the page that is open when we start the server in localhost:5000
@app.route('/')
def main():
    return render_template('search.html')


'''
---------------------------------------------------------------------------------------------
Actual API implementations
'''
@app.route('/search_movie', methods=['POST', 'GET'])
def search():
    if request.method == 'POST':
        movie = request.form['search_movie']
        url = '''https://api.themoviedb.org/3/search/movie?api_key=00e967be34501054c5adb40c77221a4c&language=en-US' 
              '&query={}&page=1&include_adult=false'''.format(
            movie)
        data = requests.get(url).json()['results']
        res = []
        for key in data:
            res.append([key['title'], key['overview'], key['id']])
        return render_template('search.html', result=res)

@app.route('/select_movie', methods=['POST', 'GET'])
def select_movie():

    movie_id = request.args['id']
    url = '''https://api.themoviedb.org/3/movie/{}/watch/providers?api_key=00e967be34501054c5adb40c77221a4c'''.format(
        movie_id)
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


'''
---------------------------------------------------------------------------------------------
Driver function
'''

if __name__ == '__main__':
    app.secret_key = 'super secret key'

    app.debug = True  # debug is used for developing since it allows us to make changes in the python file without
    # having to restart the server again and again.
    app.run(host='0.0.0.0')
