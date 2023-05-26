from email.mime.multipart import MIMEMultipart
import smtplib
from email.mime.text import MIMEText
from jinja2 import Template
import os

from helpers.model import MediaType
from helpers.recommender import topn_similar
from helpers.tmdb import fetch_media
from helpers.user import User, Settings
import pandas as pd


def get_watchlist(user_id):
    user = User.query.filter_by(id=user_id).first()
    watchlist = []

    for user_media in user.watchlist:
        watchlist.append(fetch_media(user_media.media_id, MediaType.MOVIE))

    return watchlist

def load_similarity(filepath):
    return pd.read_pickle(filepath)


DETAILS = []

SIMILARITY_MOVIE = load_similarity(os.path.join('static', 'recommender', 'similarity-5000.pkl'))


def send_email():
    sender_email = "universalstreamsearch@gmail.com"
    sender_password = "irbupoljuvsimpbu"

    with open('templates/email-template.html', 'r') as f:
        template = Template(f.read())

    for setting in DETAILS:
        print(setting.email, setting.user_id)
        watch_list = get_watchlist(setting.user_id)

        medias = [fetch_media(movies[2], MediaType.MOVIE) for movies in watch_list]

        recs = []
        for media in medias:
            if media.media_type == MediaType.MOVIE:
                similar_ids = topn_similar(SIMILARITY_MOVIE, media.id, n=10)
                for similar_id in similar_ids:
                    recs.append(fetch_media(similar_id, media.media_type))

        context = {
            'subject': 'Your recommendations from Universal Stream Search',
            'recs': recs
        }

        html = template.render(context)

        msg = MIMEMultipart('alternative')
        msg['From'] = sender_email
        msg['Subject'] = 'Your recommendations from Universal Stream Search'
        msg['To'] = setting.email
        msg.attach(MIMEText(html, 'html'))

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, setting.email, msg.as_string())
    server.quit()


import threading, time


def email_thread_1_day():
    print('details is', DETAILS)
    next_call = time.time()
    interval = 1
    while True:
        send_email()
        next_call = next_call + interval * 24 * 60 * 60;
        time.sleep(next_call - time.time())


def email_thread_7_days():
    next_call = time.time()
    interval = 7
    while True:
        send_email()
        next_call = next_call + interval * 24 * 60 * 60;
        time.sleep(next_call - time.time())


def email_thread_14_days():
    next_call = time.time()
    interval = 14
    while True:
        send_email()
        next_call = next_call + interval * 24 * 60 * 60;
        time.sleep(next_call - time.time())


def email_thread_30_days():
    next_call = time.time()
    interval = 30
    while True:
        send_email()
        next_call = next_call + interval * 24 * 60 * 60;
        time.sleep(next_call - time.time())


def start_threads(details):
    global DETAILS

    DETAILS = details

    timerThread1 = threading.Thread(target=email_thread_1_day)
    timerThread1.daemon = True
    timerThread1.start()

    timerThread2 = threading.Thread(target=email_thread_7_days)
    timerThread2.daemon = True
    timerThread2.start()

    timerThread3 = threading.Thread(target=email_thread_14_days)
    timerThread3.daemon = True
    timerThread3.start()

    timerThread4 = threading.Thread(target=email_thread_30_days)
    timerThread4.daemon = True
    timerThread4.start()