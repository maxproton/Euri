from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import service_header_requests

def get_header(domain):
    headers = {}
    if "https://" not in domain:
        domain = f"https://{domain}"

    try:
        request = Request(domain, headers=service_header_requests.request_headers())
        response = urlopen(request, timeout=20)
        headers = response.info()
    except HTTPError as e:
        print(f"[Error] HTTP error {e.code} {e.reason} trying alternative")
        return get_headers_alt(domain)
    except URLError as e:
        print(f"[Error] Url Error {e.reason}")
        return get_headers_alt(domain)
    except Exception as e:
        print(f"[Error] An unexpected error occured: {e} attempting alternative")
        return get_headers_alt(domain)

    return headers

def get_headers_alt(domain):
    headers = {}

    try:
        response = urlopen("https://" + domain,)
        headers = response.info()
    except HTTPError as e:
        print(f"[Error] HTTP error on alternative{e.code} {e.reason}")
    except URLError as e:
        print(f"[Error] Url Error on alternative{e.reason}")
    except Exception as e:
        print(f"[Error] An unexpected error occured in alternative header grab method: {e}")

    return headers

def get_cookies(header_cookie):
    cookies = {}
    for key, header in header_cookie:
        if key == 'Set-Cookie':
            pairs = header.split(",")
            pair_counter = 1
            for pair in pairs:
                try:
                    key, value = pair.split("=", 1)
                    cookies[key] = value
                except Exception:
                    cookies["confused" + str(pair_counter)] = str(pair)
                pair_counter = pair_counter + 1
        if key == 'Cookie':
            pairs = header.split(",")
            pair_counter = 1
            for pair in pairs:
                try:
                    key, value = pair.split("=", 1)
                    cookies[key] = value
                except Exception:
                    cookies["confused" + str(pair_counter)] = str(pair)
                pair_counter = pair_counter + 1

    return cookies