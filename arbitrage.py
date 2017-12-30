#logic
#For each symbol pair
# for each exchange
#  fetch symbol price
# l = get lowest ask price
# h = get highest bid price
# if h > l*1.005
# raise warning
#import ccxt.async as ccxt
#TODO implement async requests

import ccxt
import schedule, time, math
from slackclient import SlackClient
slack_token = "xoxp-290250904146-290174012755-291183230357-22369a6ca072f660db04e46cac0720da"
def job():
    ##symbols = ['BCH/USD', 'ETH/USD', 'LTC/USD', 'DASH/USD']
    sc = SlackClient(slack_token)
    global t
    t+=1
#    print t
    if (t%15 == 0) :
        sc.api_call(
            "chat.postMessage",
            channel="#alarms",
            text="Keepalive every 15 minutes")
    symbols = ['BTC', 'LTC', 'BCH', 'ETH']
    pairs = [(r,s) for s in symbols for r in symbols if r is not s]
    gdax = ccxt.gdax({'password':'', 'apiKey':'', 'secret':''})
    bitfinex = ccxt.bitfinex({'apiKey':'', 'secret':''})
    poloniex = ccxt.poloniex()
    exmo = ccxt.exmo()
    print("Connected to exchanges")
    exchanges = [ gdax, bitfinex, poloniex, exmo ]
    for r, s in pairs:
      print("Fetching values")
      findEngine(r, s, exchanges, sc)
      time.sleep(5)

def findProfit( crypto1, crypto2, exchanges):
    # There are different ways to find an opportunity, One way to classify it is on what you are pegging it against
    # 1. We could peg against bitcoin but the opportunity size must be signficant for that
    # 2. We could peg against the dollar
    # 3. We could not peg and only check if that trade even exists
    # For now I'm gonna call these: 3. Simple Engine. 2 Dollar Engine, 1 BTC Engine
    DollarEngine(crypto1, crypto2, exchanges)


def findEngine(crypto1, crypto2, exchanges, sc, extended = False):
      asks, bids ={},{}
      for x in exchanges:
        market = x.load_markets()
        #TODO perform a single fetch per exchange
        #Simple Engine, it searches for the pair directly
        #eg.: c1=LTC, c2=BTC. It checks for ltc/btc
        pair = crypto1+"/"+crypto2
        print("Checking %s on %s" %(pair, x.name))
        if pair in market.keys():
            price = x.fetch_ticker(pair)
            print(pair, price['ask'], price['bid'])
            asks[x.name] = { 'price' : price['ask'], 'symbol': pair}
            bids[x.name] = { 'price' : price['bid'], 'symbol': pair}
        ## End of simple engine. A bot with only this would run faster
        if extended:
          for peg in ['/BTC', '/USD']:
              s1=crypto1+peg
              s2=crypto2+peg
              if  not set([s1,s2]).issubset(set(market.keys())):
                  print("%s or %s not in exchange %s", s1, s2, x.name)
                  continue
              price1, price2 = x.fetch_ticker(s1), x.fetch_ticker(s2)
              print(x.name, price1['ask'], price1['bid'])
              print(x.name, price2['ask'], price2['bid'])
              price=price1['bid']/price2['ask']
              if bids.get(x.name) and bids.get(xname).get('price') < price:
                  bids[x.name]={ 'price' : price, 'symbol': (s1, s2)}
              price=price1['ask']/price2['bid']
              if asks.get(x.name) and asks.get(xname).get('price') > price:
                  asks[x.name]={ 'price' : price, 'symbol': (s1, s2)}
      if len(asks)*len(bids)==0:
          return
      askX, askPrice , askSymbol = getMin(asks) #this may not behave as expected. If so we need to create a function
      bidX, bidPrice, bidSymbol = getMax(bids)
      print(askSymbol,bidSymbol, askPrice, bidPrice, bidPrice/askPrice)
      if (bidPrice/askPrice)>1.005:
        gains=(bidPrice/askPrice-1)
        text="TEST:Opportunity found for {:.1%} gains:\n".format(gains)
        text2="Short %s on %s for %s \n" %( bidSymbol, bidX, bidPrice)
        text3="Long %s on %s for %s \n" %( askSymbol, askX, askPrice)
        #sc.api_call(
        #    "chat.postMessage",
        #    channel="#alarms",
        #    text=text+text2+text3)
        print("CONGRATS you found an opportunity")
        print(text+text2+text3)

def getMin( asks ):
    m=math.inf
    symbol=x=""
    for key, value in asks.items():
        if float(value['price']) < m:
            m,x,symbol=float(value['price']), key, value['symbol']
    return x, m, symbol

def getMax( bids ):
    m=0
    symbol=x=""
    for key, value in bids.items():
        if float(value['price']) > m:
            m,x,symbol=float(value['price']), key, value['symbol']
    return x, m, symbol


if __name__ == '__main__':
    #schedule.every(1).minutes.do(job)
    t=0
    while 1:
        job()
        #schedule.run_pending()
        time.sleep(30)
