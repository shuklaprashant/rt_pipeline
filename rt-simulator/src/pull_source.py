import requests
import json


def pull_source(url=''):

    res = requests.get(url)
    
    return json.loads(res.text)


if __name__ == '__main__':

    url = 'https://open.er-api.com/v6/latest/USD'

    print(pull_source(url))