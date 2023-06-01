import requests
import time
import json
import sys
import threading
import queue
import csv
from datetime import timedelta

API_KEY = "502ba2adb453be2c9f48a7f5137ba2f4"
append_to_response = "id,title,genres,overview,popularity" #Change this if you do not want all the data.
fields = ["id", "title", "genres", "overview", "popularity"]
BASE = "https://api.themoviedb.org/3"
DIR = "TMDBDUMP" #Directory where json files will be stored. Must exist.

class Worker(threading.Thread):
    def __init__(self, q, *args, **kwargs):
        self.q = q
        super().__init__(*args, **kwargs)

    def run(self):
        while True:
            try:
                work = self.q.get(timeout=3)  # 3s timeout
                do_work(work)
            except queue.Empty:
                return
            # do whatever work you have to do on work
            self.q.task_done()

class TMDBNotfoundException(Exception):
    """docstring for TMDBNotfoundException."""
    def __init__(self):
        super(TMDBNotfoundException, self).__init__()


def get_from_tmdb(path, query, timeout_pause = 5):
    global API_KEY, append_to_response, BASE
    url = BASE + path
    query["api_key"] = API_KEY
    r = requests.get(url, params=query, allow_redirects=True)
    if r.status_code == 404:
        raise TMDBNotfoundException()

    if "X-RateLimit-Remaining" in r.headers:
        rate_limit = r.headers["X-RateLimit-Remaining"]
        if int(rate_limit) <= 2:
            print("Request limit almost reached. Sleeping.")
            time.sleep(timeout_pause)
    else:
        time.sleep(timeout_pause)

    return r.text

def get_movie(tmdbid):
    global append_to_response, LATEST_ID
    return get_from_tmdb("/movie/{0}".format(tmdbid), {"append_to_response" : append_to_response, "language" : "en-US", "include_image_language" : "en"})

def get_latest_id():
    res = get_from_tmdb("/movie/latest", {})
    jres = json.loads(res)
    if not "id" in jres:
        time.sleep(1)
        return get_latest_id()
    return jres["id"]

LATEST_ID = get_latest_id()

def do_update_latest_id():
    global LATEST_ID, q
    while not q.empty():
        lid = get_latest_id()
        if lid != LATEST_ID:
            print("Updating latest id from {0} to {1}".format(LATEST_ID, lid))
            for newId in range(LATEST_ID+1, lid+1):
                q.put_nowait(newId)

            LATEST_ID = lid
        time.sleep(200)


def do_work(tmdbid):
    global LATEST_ID, start, fromId
    try:
        res = get_movie(tmdbid)
        jres = json.loads(res)

        if "id" not in jres:
            time.sleep(1)
            do_work(tmdbid)
            return
        # with open("dump/movies.csv", "a") as f:
        #     f.write(jres["title"], jres["genres"], jres["overview"], jres["popularity"])

        with open('../dump/movies.csv', 'a', newline='') as csvfile:
            # Create a CSV writer object
            writer = csv.writer(csvfile)

            # Write data rows
            writer.writerow([jres[field] for field in fields])
            

        current = time.time()
        difference = float(current - start) / float(tmdbid - fromId + 1)
        eta = (LATEST_ID - tmdbid) * difference
        print("Downloaded data for movie {0} ({1}).".format(jres["original_title"], tmdbid))
        print("\t  {0}/{1} (Total: {2}/{3}), {4} left.".format(tmdbid - fromId + 1, LATEST_ID-fromId + 1, tmdbid, LATEST_ID, str(timedelta(seconds=eta))))
    except TMDBNotfoundException as e:
        print("No movie with TMDBID {0} found".format(tmdbid))

def download_all_json():
    global LATEST_ID, start, fromId, q
    tmdbid = fromId
    start = time.time()
    q = queue.Queue()
    for tmdbid in range(fromId, LATEST_ID+1):
        q.put_nowait(tmdbid)

    for _ in range(10):
        Worker(q).start()
    try:
        t = threading.Thread(target=do_update_latest_id)
        t.start()
        q.join()
    except Exception as e:
        with q.mutex:
            q.queue.clear()
        raise e
    # try:
    #     while True:
    #
    #         tmdbid += 1
    #         if tmdbid >= LATEST_ID-2:
    #             LATEST_ID = get_latest_id()
    # except Exception as e:
    #     print(e)
    #     print("Last TMDBID was: {0}".format(tmdbid))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        fromId = 1
        download_all_json()
    else:
        fromId = int(sys.argv[1])
        download_all_json()