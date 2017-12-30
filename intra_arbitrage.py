import ccxt

# from fiat_normalizer import fixerio
from fixerio import fixerio

FIAT = ['EUR', 'USD', 'JPY', 'GBP', 'CAD']


def fiat_markets():
    """ Retrieves all tickers from an exchange (Kraken for now) and returns only fiat markets """
    kraken = ccxt.kraken()
    tickers = kraken.fetch_tickers()
    fiat_tickers = [tickers[x] for x in tickers for y in FIAT if y in tickers[x]['symbol']]
    return fiat_tickers


def all_markets():
    """ Retrieves all tickers from an exchange (Kraken for now) and returns them """
    kraken = ccxt.kraken()
    tickers = kraken.fetch_tickers()
    tickers = [tickers[x] for x in tickers]
    # print(tickers)
    return tickers


def parse_tickers(usdprice, data):
    """ Input should be a dictionary with all the information for a ticker
     such as what is returned form the fiat_markets module

     return is a dictionary with base, dest, ask and price_usd
     """
    parsed = dict()
    # print(data)
    parsed['base'], parsed['dest'] = data['symbol'].strip().split('/')
    parsed['ask'] = data['ask']
    parsed['bid'] = data['bid']
    parsed['ask_usd'] = price_in_usd(usdprice, parsed['ask'], parsed['dest'])
    parsed['bid_usd'] = price_in_usd(usdprice, parsed['bid'], parsed['dest'])
    # parsed['price_usd'] = price_in_usd(parsed['ask'], parsed['dest'])
    return parsed


def price_in_usd(usdprice, amount, base, dest='USD'):
    # print(amount, base, dest)
    """ Return price of any "dest" currency normalized to USD """
    return usdprice.convert(amount, base=base, dest=dest)


def find_opportunities(data):
    opportunities = []
    found = False
    # print(data)
    for x in data:
        for i, y in enumerate(data[x]):
            j = i + 1
            while j < len(data[x]):
                # print (data[x][i],data[x][j])
                if data[x][i]['ask_usd'] < data[x][j]['bid_usd']:
                    lower = float(data[x][i]['ask_usd'])
                    higher = float(data[x][j]['bid_usd'])
                    lower_fiat = data[x][i]['dest']
                    higher_fiat = data[x][j]['dest']
                    found = True
                elif data[x][i]['bid_usd'] > data[x][j]['ask_usd']:
                    higher = float(data[x][i]['bid_usd'])
                    lower = float(data[x][j]['ask_usd'])
                    lower_fiat = data[x][j]['dest']
                    higher_fiat = data[x][i]['dest']
                    found = True
                # else:
                #     j += 1
                #     continue
                # print(higher, lower)
                if found:
                    opportunity = dict()
                    opportunity['lower'] = lower
                    opportunity['higher'] = higher
                    opportunity['lower_fiat'] = lower_fiat
                    opportunity['higher_fiat'] = higher_fiat
                    opportunity['price_diff'] = higher - lower
                    opportunity['price_diff_percent'] = higher / lower
                    opportunity['crypto'] = x
                    found = False
                    opportunities.append(opportunity.copy())
                    opportunity.clear()
                j += 1
    return opportunities


def calculate_profit(opport):
    result = list()
    profit_dict = dict()
    cryptoB = None
    pairs = None
    found = False
    for i, x in enumerate(opport):
        j = i + 1
        while j < len(opport):
            # print (opport[i]['lower_fiat'], opport[i]['higher_fiat'])
            # print (opport[j]['lower_fiat'], opport[j]['higher_fiat'])
            # print(((opport[i]['lower_fiat'] == opport[j]['lower_fiat'])
            #     or (opport[i]['lower_fiat'] == opport[j]['higher_fiat'])))
            # print(((opport[i]['higher_fiat'] == opport[j]['lower_fiat'])
            #     or (opport[i]['higher_fiat'] == opport[j]['higher_fiat'])))
            if (((opport[i]['lower_fiat'] == opport[j]['lower_fiat'])
                or (opport[i]['lower_fiat'] == opport[j]['higher_fiat']))
                and ((opport[i]['higher_fiat'] == opport[j]['lower_fiat'])
                or (opport[i]['higher_fiat'] == opport[j]['higher_fiat']))):
                if opport[i]['price_diff_percent'] > opport[j]['price_diff_percent']:
                    profit = opport[i]['price_diff_percent'] - opport[j]['price_diff_percent'] -.005
                    Abuy = opport[i]['lower_fiat']
                    Asell = opport[i]['higher_fiat']
                    Bbuy = opport[j]['lower_fiat']
                    Bsell = opport[j]['higher_fiat']
                    cryptoB = opport[j]['crypto']
                    # pairs = [opport[i]['lower_fiat'], opport[i]['higher_fiat'],
                    #          opport[j]['lower_fiat'], opport[j]['higher_fiat']]
                    found = True
                else:
                    profit = opport[j]['price_diff_percent'] - opport[i]['price_diff_percent'] -.005
                    Abuy = opport[i]['lower_fiat']
                    Asell = opport[i]['higher_fiat']
                    Bbuy = opport[j]['lower_fiat']
                    Bsell = opport[j]['higher_fiat']
                    cryptoB = opport[j]['crypto']
                    # pairs = [opport[i]['lower_fiat'], opport[i]['higher_fiat'],
                    #          opport[j]['lower_fiat'], opport[j]['higher_fiat']]
                    found = True
            j += 1
            if found:

                profit_dict['profit_percent'] = profit
                profit_dict['cryptoA'] = opport[i]['crypto']
                # profit_dict['cryptoB'] = opport[j]['crypto']
                profit_dict['Abuy'] = Abuy
                profit_dict['Asell'] = Asell
                profit_dict['Bbuy'] = Bbuy
                profit_dict['Bsell'] = Bsell
                profit_dict['cryptoB'] = cryptoB
                profit_dict['base'] = opport[i]['lower_fiat']
                profit_dict['dest'] = opport[i]['higher_fiat']
                # profit_dict['pairs'] = pairs
                # result.append(opport[i])
                # result.append(opport[j-1])
                result.append(profit_dict.copy())
                profit_dict.clear()
                cryptoB = None
                # pairs = None
                found = False
    return result


def main():
    usdprice = fixerio.Fixerio()
    for x in FIAT:
        usdprice.get_rates(base=x)
        # print(usdprice._cache)
    parsed_tickers = dict()
    markets = fiat_markets()
    # print(markets)
    for x in markets:
        # print(x)
        response = parse_tickers(usdprice, x)
        if response['base'] not in parsed_tickers:
            parsed_tickers[response['base']] = []
        parsed_tickers[response['base']].append(response)
    # for x in parsed_tickers:
    #     print(x)
    #     for y in parsed_tickers[x]:
    #         print(str(y['dest']) + ' : ' + str(y['price_usd']))
    # print(parsed_tickers)
    opportunities = find_opportunities(parsed_tickers)
    print(*opportunities, sep='\n')
    profit = calculate_profit(opportunities)
    print(*profit, sep='\n')
    # print(*opportunities, sep='\n\n')


if __name__ == '__main__':
    main()
