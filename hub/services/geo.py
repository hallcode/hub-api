import requests
import urllib


def post_code_check(post_code):
    pc = urllib.parse.quote(post_Code)
    r = requests.get('https://api.postcodes.io/postcodes/{:s}'.format(pc))

    if r.status_code == 404:
        return None

    if r.status_code != 200:
        raise Exception

    return r.json()['codes']
    