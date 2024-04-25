import os

import requests
from dotenv import load_dotenv

load_dotenv()


def get_iam_token():
    yandex_passport_oauth_token = os.getenv("OAUTH_TOKEN")
    data = {"yandexPassportOauthToken": str(yandex_passport_oauth_token)}
    url = "https://iam.api.cloud.yandex.net/iam/v1/tokens"
    answer = requests.post(url, json=data)
    return answer.json().get("iamToken")
