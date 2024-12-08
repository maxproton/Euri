from urllib.request import urlopen
import requests


def get_header(domain):
    headers = {}
    try:
        response = urlopen("https://" + domain)
        headers = response.info()
    except requests.exceptions.Timeout:
        print("[Error] Request header timed out")
    except requests.exceptions.RequestException as e:
        print(f"[Error] Erro while getting headers {e}")

    return headers