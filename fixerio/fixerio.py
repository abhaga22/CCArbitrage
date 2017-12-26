import requests

BASE_URL = 'https://api.fixer.io/'
LATEST = 'latest'
DEFAULT_BASE = 'USD'


def get_rates(date: str=LATEST, base: str=DEFAULT_BASE, symbols: str=None) -> dict:
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
        raise Exception("""
        Check your input and try again
        
        date: OPTIONAL type str
            a date form January 4th 1999 to today in the format 'yyyy-mm-dd'
            or 'latest'. If omitted, 'latest' is used. 

        base: OPTIONAL type str
            a 3 letter currency code such as 'EUR'. If omitted, 'USD' is used.

        symbols: OPTIONAL type str
            a string of comma separated currency codes like 'USD,JPY,EUR'. If
            omitted, all rates are returned for the corresponding base and date.
        """)


def convert(amount: float, base: str=DEFAULT_BASE, dest: str=None) -> float:
    """ Converts an amount from the base currency to the symbols currency """
    try:
        if base == dest:
            return amount
        conversion_rate = get_rates(date=LATEST, base=base, symbols=dest)
        return float(amount) * conversion_rate[dest]
    except Exception:
        raise Exception("""
        Check your input and try again
        
        amount: REQUIRED type int or str
            an integer amount of the base currency to convert.

        base: OPTIONAL type str
            a 3 letter currency code such as 'EUR'. If omitted, 'USD' is used.

        symbols: REQUIRED type str
            a 3 letter currency code such as 'JPY'.
        """)
