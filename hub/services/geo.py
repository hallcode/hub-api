import requests
import urllib


def post_code_check(post_code):
    if post_code is None:
        return
        
    pc = urllib.parse.quote(post_code)
    r = requests.get('https://api.postcodes.io/postcodes/{:s}'.format(pc))

    if r.status_code == 404:
        return None

    if r.status_code != 200:
        raise Exception

    json = r.json()
    return json['result']['codes']
    