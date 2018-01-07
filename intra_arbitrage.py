import ccxt

# from fiat_normalizer import fixerio
from fixerio import fixerio

FIAT = {'EUR', 'USD', 'JPY', 'GBP', 'CAD'}


def fiat_markets():
    """ Retrieves all tickers from an exchange (Kraken for now) and returns only fiat markets """
    kraken = ccxt.kraken()
    tickers = kraken.fetch_tickers()
    fiat_tickers = []
    crypto_tickers = []
    for x in tickers:
        if tickers[x]['symbol'].split('/')[1] in FIAT:
            fiat_tickers.append(tickers[x])
        else:
            crypto_tickers.append(tickers[x])
    # fiat_tickers = [tickers[x] for x in tickers for y in FIAT if y in tickers[x]['symbol']]
    # print(fiat_tickers)
    return fiat_tickers, crypto_tickers


# def all_markets():
#     """ Retrieves all tickers from an exchange (Kraken for now) and returns them """
#     kraken = ccxt.kraken()
#     tickers = kraken.fetch_tickers()
#     tickers = [tickers[x] for x in tickers]
#     # print(tickers)
#     return tickers


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


def parse_crypto_tickers(crypto_prices, data):
    """ Input should be a dictionary with all the information for a ticker
     such as what is returned form the fiat_markets module

     return is a dictionary with base, dest, ask and price_usd
     """
    parsed = dict()
    # print(data)
    parsed['base'], parsed['dest'] = data['symbol'].strip().split('/')
    parsed['ask'] = data['ask']
    parsed['bid'] = data['bid']
    parsed['ask_usd'] = crypto_price_in_usd(crypto_prices, parsed['ask'], parsed['dest'])
    parsed['bid_usd'] = crypto_price_in_usd(crypto_prices, parsed['bid'], parsed['dest'])
    # parsed['price_usd'] = price_in_usd(parsed['ask'], parsed['dest'])
    # print(parsed)
    return parsed.copy()


def price_in_usd(usdprice, amount, base, dest='USD'):
    # print(amount, base, dest)
    """ Return price of any "dest" currency normalized to USD """
    return usdprice.convert(amount, base=base, dest=dest)


def crypto_price_in_usd(crypto_prices, amount, base):
    # print(amount, base, dest)
    """ Return price of any "dest" currency normalized to USD """
    # if parsed_tickers['base']
    return crypto_prices[base] * amount


def find_opportunities(data):
    opportunities = []
    opportunities_loss = []
    found1 = False
    found2 = False
    # print(data)
    for x in data:
        # print('here!!1')
        for i, y in enumerate(data[x]):
            # print('here!!!2')
            j = i + 1
            while j < len(data[x]):
                # print('here!!!3')
                # print (data[x][i],data[x][j])
                if data[x][i]['ask_usd'] < data[x][j]['bid_usd']:
                    higher = float(data[x][j]['bid_usd'])
                    lower = float(data[x][i]['ask_usd'])
                    higher_fiat = data[x][j]['dest']
                    lower_fiat = data[x][i]['dest']
                    found1 = True
                elif data[x][i]['bid_usd'] > data[x][j]['ask_usd']:
                    higher = float(data[x][i]['bid_usd'])
                    lower = float(data[x][j]['ask_usd'])
                    higher_fiat = data[x][i]['dest']
                    lower_fiat = data[x][j]['dest']
                    found1 = True
                elif data[x][i]['ask_usd'] >= data[x][j]['bid_usd']:
                    higher = float(data[x][i]['ask_usd'])
                    lower = float(data[x][j]['bid_usd'])
                    higher_fiat = data[x][i]['dest']
                    lower_fiat = data[x][j]['dest']
                    found2 = True
                elif data[x][i]['bid_usd'] <= data[x][j]['ask_usd']:
                    higher = float(data[x][j]['bid_usd'])
                    lower = float(data[x][i]['ask_usd'])
                    higher_fiat = data[x][j]['dest']
                    lower_fiat = data[x][i]['dest']
                    found2 = True
                # else:
                #     j += 1
                #     continue
                # print(higher, lower)
                if found1:
                    opportunity = dict()
                    opportunity['lower'] = lower
                    opportunity['higher'] = higher
                    opportunity['lower_fiat'] = lower_fiat
                    opportunity['higher_fiat'] = higher_fiat
                    opportunity['price_diff_usd'] = higher - lower
                    opportunity['price_diff_percent'] = higher / lower
                    opportunity['crypto'] = x
                    opportunity['profit'] = True
                    found1 = False
                    opportunities.append(opportunity.copy())
                    opportunity.clear()
                elif found2:
                    opportunity_loss = dict()
                    opportunity_loss['lower'] = lower
                    opportunity_loss['higher'] = higher
                    opportunity_loss['lower_fiat'] = lower_fiat
                    opportunity_loss['higher_fiat'] = higher_fiat
                    opportunity_loss['price_diff_usd'] = lower - higher
                    opportunity_loss['price_diff_percent'] = (lower / higher) - 1
                    opportunity_loss['crypto'] = x
                    opportunity_loss['profit'] = False
                    found2 = False
                    opportunities_loss.append(opportunity_loss.copy())
                    opportunity_loss.clear()
                j += 1
    return opportunities, opportunities_loss


def calculate_profit(opport):
    result = list()
    profit = 0
    profit_dict = dict()
    cryptoB = None
    # pairs = None
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
            if ((opport[i]['lower_fiat'] == opport[j]['higher_fiat'])
                # or (opport[i]['lower_fiat'] == opport[j]['lower_fiat']))
                and (opport[i]['higher_fiat'] == opport[j]['lower_fiat'])):
                # or (opport[i]['higher_fiat'] == opport[j]['higher_fiat']))):
                # if opport[i]['price_diff_percent'] > opport[j]['price_diff_percent']:
                profit = opport[i]['price_diff_percent'] + opport[j]['price_diff_percent'] - 2.005
                Abuy = opport[i]['lower_fiat']
                Asell = opport[i]['higher_fiat']
                Bbuy = opport[j]['lower_fiat']
                Bsell = opport[j]['higher_fiat']
                cryptoA = opport[i]['crypto']
                cryptoB = opport[j]['crypto']
                # pairs = [opport[i]['lower_fiat'], opport[i]['higher_fiat'],
                #          opport[j]['lower_fiat'], opport[j]['higher_fiat']]
                found = True
                # else:
            elif ((opport[i]['lower_fiat'] == opport[j]['lower_fiat'])
                # or (opport[i]['lower_fiat'] == opport[j]['lower_fiat']))
                and (opport[i]['higher_fiat'] == opport[j]['higher_fiat'])):
                if opport[j]['price_diff_percent'] > opport[i]['price_diff_percent']:
                    profit = opport[j]['price_diff_percent'] - opport[i]['price_diff_percent'] - .005
                    Abuy = opport[j]['lower_fiat']
                    Asell = opport[j]['higher_fiat']
                    Bbuy = opport[i]['higher_fiat']
                    Bsell = opport[i]['lower_fiat']
                    cryptoA = opport[j]['crypto']
                    cryptoB = opport[i]['crypto']
                    found = True
                else:
                    profit = opport[i]['price_diff_percent'] - opport[j]['price_diff_percent'] - .005
                    Abuy = opport[i]['lower_fiat']
                    Asell = opport[i]['higher_fiat']
                    Bbuy = opport[j]['higher_fiat']
                    Bsell = opport[j]['lower_fiat']
                    cryptoA = opport[i]['crypto']
                    cryptoB = opport[j]['crypto']
                    found = True
            # else:
            #     print(opport[i], opport[j], sep='\n')
            #     print('*********************************************************************************************')
                # pairs = [opport[i]['lower_fiat'], opport[i]['higher_fiat'],
                #          opport[j]['lower_fiat'], opport[j]['higher_fiat']]
                # found = True
            j += 1
            if found & (profit > 0.001):

                profit_dict['profit_percent'] = profit
                profit_dict['cryptoA'] = cryptoA
                # profit_dict['cryptoB'] = opport[j]['crypto']
                profit_dict['Abuy'] = Abuy
                profit_dict['Asell'] = Asell
                profit_dict['Bbuy'] = Bbuy
                profit_dict['Bsell'] = Bsell
                profit_dict['cryptoB'] = cryptoB
                # profit_dict['base'] = opport[i]['lower_fiat']
                # profit_dict['dest'] = opport[i]['higher_fiat']
                # profit_dict['pairs'] = pairs
                # result.append(opport[i])
                # result.append(opport[j-1])
                result.append(profit_dict.copy())
                profit_dict.clear()
                profit = 0
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
    crypto_prices = dict()
    markets, crypto_markets = fiat_markets()
    # print(crypto_markets)
    for x in markets:
        # print(x)
        # print('here!!!')
        response = parse_tickers(usdprice, x)
        if response['base'] not in parsed_tickers:
            parsed_tickers[response['base']] = []
        parsed_tickers[response['base']].append(response)
        if ((response['base'] == 'BTC') and (response['dest'] == 'USD')
            or (response['base'] == 'ETH') and (response['dest'] == 'USD')):
            # crypto_prices['base'] = response['base']
            # crypto_prices['ask'] = response['ask']
            # crypto_prices[response['base']] = response['ask']
            crypto_prices[response['base']] = response['bid']
    # print(crypto_prices)
    # print(parsed_tickers)
    for x in crypto_markets:
        # print(x)
        response_c = parse_crypto_tickers(crypto_prices, x)
        # print(response)
        if response_c['base'] not in parsed_tickers:
            parsed_tickers[response_c['base']] = []
        parsed_tickers[response_c['base']].append(response_c)
    # print('((((((((((((((((((((((((((((((((((((((((')
    # print(parsed_tickers)
    # print('))))))))))))))))))))))))))))))))))))))))')
    # for x in parsed_tickers:
    #     print(x)
    #     for y in parsed_tickers[x]:
    #         print(str(y['dest']) + ' : ' + str(y['price_usd']))
    # print(parsed_tickers)
    # print(parsed_tickers, sep='\n\n')


    opportunities, opportunities_loss = find_opportunities(parsed_tickers)
    print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
    print(*opportunities, sep='\n')
    print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
    print(*opportunities_loss, sep='\n')
    print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
    profit = calculate_profit(opportunities)
    print(*profit, sep='\n\n')
    # print(*opportunities, sep='\n\n')


if __name__ == '__main__':
    main()


# OPPORTUNITIES MODULE: record negative opportunities
#TODO CALCULATE_PROFIT MODULE: find cheapest way to return money to initial currency
# integrate cryptos to the conversions (bid price of BTC or ETH becomes the ask price of "random crypto")
