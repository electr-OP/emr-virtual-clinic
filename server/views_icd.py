import requests


def get_search():
    token_endpoint = 'https://icdaccessmanagement.who.int/connect/token'
    client_id = '3dc12fda-0dcb-448b-80c8-c5cfd60524f7_20c9745a-402c-42b7-ba68-1fe60a107788'
    client_secret = 'KmwBZPjU5CsSMuCpanNrQYdlGiAPQdafIuYDxl6ZMQg='
    scope = 'icdapi_access'
    grant_type = 'client_credentials'

    # get the OAUTH2 token

    # set data to post
    payload = {'client_id': client_id,
               'client_secret': client_secret,
               'scope': scope,
               'grant_type': grant_type}

    # make request
    r = requests.post(token_endpoint, data=payload, verify=False).json()
    token = r['access_token']

    # access ICD API

    uri = 'https://id.who.int/icd/entity'

    # HTTP header fields to set
    headers = {'Authorization': 'Bearer ' + token,
               'Accept': 'application/json',
               'Accept-Language': 'en',
               'API-Version': 'v2'}

    # make request
    r = requests.get(uri, headers=headers, verify=False)

    # print the result
    print(r.text)