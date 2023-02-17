#! /bin/python3

TOKEN_PATH = "token.json"
APP_NAME = "ShikimoriToScs"
CLIENT_ID = "5GufR7epCg2Wr9QKVyfC8wVv51SAi8o2iHPavcrQ3k4"
CLIENT_SECRET = "ckMcJpsJOubv4raN7hlaz1jIkLxTl7hT08OUYDzEGCc"

MAX_RETRIES = 1000
OUTPUT_FILE = "ranobes.json"
SORT_ORDER = "ranked"


from shikimori_api import Shikimori
import json
from requests.exceptions import HTTPError
from requests.models import Response

class Genre:

    def __init__(self, raw: dict) -> None:
        self.name = raw["name"]
        self.russian_name = raw["russian"]
        self.kind = raw["kind"]

    def __repr__(self) -> str:
        return f"Genre(name={self.name}, russian_name={self.russian_name}, kind={self.kind})"


class Ranobe:

    def __init__(self, raw: dict) -> None:
        self.name = raw["name"]
        self.russian_name = raw["russian"]
        self.released_on = raw["released_on"]
        self.genres = list(map(lambda x: Genre(x), raw["genres"]))
        self.publishers = list(map(lambda x: x['name'], raw["publishers"]))
        self.description = raw["description"]
        self.description_html = raw["description_html"]


def token_saver(token: dict):
    with open('token.json', 'w') as f:
        f.write(json.dumps(token))


def load_token(path: str):
    with open(path) as f:
        return json.load(f)


def get_api(app_name: str, client_id: str, client_secret: str, token_path: str, token_saver):
    session = Shikimori(app_name,
                        client_id=client_id,
                        client_secret=client_secret,
                        token=load_token(token_path),
                        token_saver=token_saver)
    return session.get_api()


def get_ranobes(api, limit: int = 50, offset: int = 0, order: str = "ranked"):
    return api.ranobe.GET(limit=50, order=order, offset=offset)


def get_many_ranobes(api, pages: int = 6, order: str = "ranked"):
    ranobes = []
    for i in range(pages):
        fetched = False
        for j in range(MAX_RETRIES):
            try:
                ranobes += get_ranobes(api, limit=50, offset=i*50, order=order)
                fetched = True
                break
            except HTTPError as e:
                response: Response = e.response
                if response.status_code == 429:
                    continue
                else:
                    print(f"Unknown error: {response.status_code}, {response.content}")
                    exit(1)
        if not fetched:
            print(f"Failed to fetch ranobe page with number {i}")
    return ranobes


def main():
    api = get_api(APP_NAME, CLIENT_ID, CLIENT_SECRET, TOKEN_PATH, token_saver)
    ranobes = get_many_ranobes(api, pages=6, order=SORT_ORDER)

    id_list = list(map(lambda x: x["id"], ranobes))

    ranobe_details = []
    for id in id_list:
        fetched = False
        for i in range(MAX_RETRIES):
            try:
                ranobe_details.append(api.ranobe(id).GET())
                fetched = True
                break
            except HTTPError as e:
                response: Response = e.response
                if response.status_code == 429:
                    continue
                else:
                    print(f"Unknown error: {response.status_code}, {response.content}")
                    exit(1)
        if not fetched:
            print(f"Failed to fetch ranobe with id {id}")

    ranobes = list(map(lambda x: Ranobe(x), ranobe_details))
    with open(OUTPUT_FILE, "w") as file:
        file.write(json.dumps(ranobes, default=lambda o: o.__dict__, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    main()
