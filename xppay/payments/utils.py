import requests


def xp2jpy():
    response = requests.get('https://api.coinmarketcap.com/v1/ticker/xp/?convert=JPY').json()
    return {'price_jpy': response[0]['price_jpy'], 'last_updated': response[0]['last_updated']}
