import requests

def get(url, body=None, headers=None):
    return requests.get(
        url,
        headers = headers,
        body = body
    )

def post(url, body=None, headers=None):
    return requests.post(
        url,
        headers = headers,
        body = body
    )

def put(url, body=None, headers=None):
    return requests.put(
        url,
        headers = headers,
        body = body
    )

def delete(url, body=None, headers=None):
    return requests.delete(
        url,
        headers = headers,
        body = body
    )