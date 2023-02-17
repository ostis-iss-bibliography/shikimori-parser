#! /bin/python3

from shikimori_api import Shikimori
import json
import time
from requests.exceptions import HTTPError
from requests.models import Response

def token_saver(token: dict):
    with open('token.json', 'w') as f:
        f.write(json.dumps(token))

with open('token.json') as f:
    token = json.load(f)

session = Shikimori("Tournament",
                    client_id="5GufR7epCg2Wr9QKVyfC8wVv51SAi8o2iHPavcrQ3k4",
                    client_secret="ckMcJpsJOubv4raN7hlaz1jIkLxTl7hT08OUYDzEGCc",
                    token=token,
                    token_saver=token_saver)

api = session.get_api()

ranobes = api.ranobe.GET(limit=250, order="ranked")

id_list = list(map(lambda x: x["id"], ranobes))

for id in id_list:
    try:
        ran = api.ranobe(id).GET()
    except Exception as e:
        print(e)

    print(f"{ran['name']} \ {ran['russian']} \ {ran['released_on']} \ {ran['genres'][0]['name']} \ {ran['publishers']}")
