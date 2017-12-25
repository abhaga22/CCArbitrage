import requests

BASE_URL = 'https://api.fixer.io/'
LATEST = 'latest'
DEFAULT_BASE = 'USD'


def get_rates(date=LATEST, base=DEFAULT_BASE, symbols=None):
    try:
        url = BASE_URL + date
        if symbols is None:
            payload = dict(base=base)
        else:
            payload = dict(base=base, symbols=symbols)
        response = requests.get(url, params=payload)
        json_data = response.json()
        return json_data['rates']
    except Exception:
        raise Exception(""" \nCheck your input and try again
        date: 
            a date form January 4th 1999 to today in the format 'yyyy-mm-dd'

        base:
            a 3 letter currency code like 'USD'

        symbols
            a string of comma separated currency codes like 'USD,JPY,EUR'
        """)


def convert(amount, base='USD', symbols=None):
    """ Converts an amount from the base currency to the symbols currency """
    try:
        conversion_rate = get_rates(date=LATEST, base=base, symbols=symbols)
        return amount * conversion_rate[symbols]
    except Exception:
        raise Exception("""\nCheck your input and try again
        date: 
            a date form January 4th 1999 to today in the format 'yyyy-mm-dd'

        base:
            a 3 letter currency code like 'USD'

        symbols
            a 3 letter currency code like 'JPY'
        """)


def main():
    """ Usage examples """
    response = convert(10, base='USD', symbols='EUR')
    print(response, end='\n\n')
    response = get_rates(symbols='JPY')
    print(response, end='\n\n')
    response = get_rates(base='EUR', symbols=None)
    print(response, end='\n\n')
    response = get_rates(date='latest', base='USD', symbols='EUR,JPY')
    print(response, end='\n\n')


if __name__ == '__main__': main()