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

import ccxt, sys
import schedule, time, math, json
from slackclient import SlackClient
slack_token = "xoxp-290250904146-290174012755-291183230357-22369a6ca072f660db04e46cac0720da"
amount={'BCH/USD':0.009,
        'LTC/USD':0.1,
        'ETH/USD':0.025,
        'DASH/USD':0.02}
tokens={}
def job(args={}):
    ##symbols = ['BCH/USD', 'ETH/USD', 'LTC/USD', 'DASH/USD']
    sc = SlackClient(slack_token)
    global t
    t+=1
#    print t
    #if (t%15 == 0) :
    #    sc.api_call(
    #        "chat.postMessage",
    #        channel="#alarms",
    #        text="Keepalive every 15 minutes")
    symbols = ['LTC', 'BCH', 'ETH', 'DASH']
    pairs = [(r,s) for s in symbols for r in symbols if r is not s]
    gdax = ccxt.gdax(args['gdax'])
    bitfinex = ccxt.bitfinex(args['bitfinex'])
    poloniex = ccxt.poloniex()
    bittrex = ccxt.bittrex()
    exmo = ccxt.exmo()
    print("Connected to exchanges")
    exchanges = [ gdax, bitfinex ]
    for r, s in pairs:
      print("Fetching values")
      findEngine(r, s, exchanges, sc, True)
      time.sleep(15)

def findProfit( crypto1, crypto2, exchanges):
    # There are different ways to find an opportunity, One way to classify it is on what you are pegging it against
    # 1. We could peg against bitcoin but the opportunity size must be signficant for that
    # 2. We could peg against the dollar
    # 3. We could not peg and only check if that trade even exists
    # For now I'm gonna call these: 3. Simple Engine. 2 Dollar Engine, 1 BTC Engine
    DollarEngine(crypto1, crypto2, exchanges)


def findEngine(crypto1, crypto2, exchanges, sc, extended = False):
      asks, bids ={},{}
      name={}
      for x in exchanges:
        name[x.name]=x
      for x in exchanges:
        market = x.load_markets()
        #TODO perform a single fetch per exchange
        #Simple Engine, it searches for the pair directly
        #eg.: c1=LTC, c2=BTC. It checks for ltc/btc
        pair = crypto1+"/"+crypto2
        print("Checking %s on %s" %(pair, x.name))
        #if pair in market.keys():
        #    price = x.fetch_ticker(pair)
        #    print(pair, price['ask'], price['bid'])
        #    asks[x.name] = { 'price' : price['ask'], 'symbol': (pair)}
        #    bids[x.name] = { 'price' : price['bid'], 'symbol': (pair)}
        ## End of simple engine. A bot with only this would run faster
        if extended:
          for peg in ['/USD']:
              s1=crypto1+peg
              s2=crypto2+peg
              if  not set([s1,s2]).issubset(set(market.keys())):
                  print("%s or %s not in %s"% (s1, s2, x.name))
                  continue
              price1, price2 = x.fetch_ticker(s1), x.fetch_ticker(s2)
              #print(x.name, s1, price1['ask'], price1['bid'])
              #print(x.name, s2, price2['ask'], price2['bid'])
              price=price1['bid']/price2['ask']
              bid=price
              if bids.get(x.name) and bids.get(x.name).get('price') < price:
                  bids[x.name]={ 'price' : price, 'symbol': (s1, s2)}
              else:
                  bids[x.name]={ 'price' : price, 'symbol': (s1, s2)}
              price=price1['ask']/price2['bid']
              print(x.name, s1, "/", s2, "{:02.5f}".format(bid), "{:02.5f}".format(price))
              if asks.get(x.name) and asks.get(x.name).get('price') > price:
                  asks[x.name]={ 'price' : price, 'symbol': (s1, s2)}
              else:
                  asks[x.name]={ 'price' : price, 'symbol': (s1, s2)}
      if len(asks)*len(bids)==0:
          return
      print("RESULTS:")
      askX, askPrice , askSymbol = getMin(asks) #this may not behave as expected. If so we need to create a function
      bidX, bidPrice, bidSymbol = getMax(bids)
      print(askSymbol,bidSymbol,"{:02.5f}".format(askPrice),
            "{:02.5f}".format(bidPrice), "{:02.5f}".format(bidPrice/askPrice))
      #TODO incorporate logic for fees
      if (bidPrice/askPrice)>1.01:
        gains=(bidPrice/askPrice-1)
        text="Opportunity found for {:.1%} gains:\n".format(gains)
        text+="Sell %s on %s " %( bidSymbol[0], bidX)
        if len(bidSymbol)>1:
            text+= ",Buy %s on %s " %( bidSymbol[1], bidX)
        text+="for {:02.5f} \n".format(bidPrice)
        text+="Buy %s on %s " %( askSymbol[0], askX)
        if len(askSymbol)>1:
            text+= ",Sell %s on %s " %( askSymbol[1], askX)
        text+="for {:02.5f} \n".format(askPrice)
        #sc.api_call(
        #    "chat.postMessage",
        #    channel="#alarms",
        #    text=text)
        print("CONGRATS you found an opportunity")
        print(text)
        execute(name[askX], name[bidX], askSymbol[0], askSymbol[1])

def execute(askX=None, bidX=None, s1='BCH/USD', s2='LTC/USD'):
    #0 get balance
    #determine amount of transaction
    #1.Buy s1 on at askX
    #2 Sell s1 at bidX
    #3.Buy s2 on bidX
    #4.sell s2 on askX
    #5.get balance
    global amount
    beforeX1=askX.fetch_balance()
    beforeX2=bidX.fetch_balance()
    price=askX.fetch_ticker(s1)
    price['bid'] = max(price['ask']-0.01, price['bid'])
    print(askX.name,s1,'limit','buy',amount[s1],"{:02.2f}".format(price['bid']))
    usd=amount[s1]*float(price['bid'])
    askX.create_order(s1,'limit','buy', "{:02.5f}".format(amount[s1]*1.002),
               "{:02.2f}".format(price['bid']))
    price=bidX.fetch_ticker(s1)
    price['ask'] = min(price['bid']+0.01, price['ask'])
    print(bidX.name, s1, 'limit', 'sell', amount[s1], "{:02.2f}".format(price['ask']))
    bidX.create_order(s1,'limit','sell', amount[s1],
               "{:02.2f}".format(price['ask']))
    price=bidX.fetch_ticker(s2)
    price['bid'] = max(price['ask']-0.01, price['bid'])
    amount[s2]=usd/float(price['bid'])
    print(bidX.name,s2, 'limit', 'buy',
      "{:02.5f}".format(amount[s2]),
      "{:02.2f}".format(price['bid']))
    bidX.create_order(s2,'limit','buy', "{:02.5f}".format(amount[s2]*1.002),
               "{:02.2f}".format(price['bid']))
    price=askX.fetch_ticker(s2)
    price['ask'] = min(price['bid']+0.01, price['ask'])
    print(askX.name, s2, 'limit', 'sell',
      "{:02.5f}".format(amount[s2]),
      "{:02.2f}".format(price['ask']))
    askX.create_order(s2,'limit','sell', "{:02.5f}".format(amount[s2]),
               "{:02.2f}".format(price['ask']))
    #wait for transaction to clear:
    while(len(askX.fetch_open_orders())+len(bidX.fetch_open_orders())):
         time.sleep(15)
    afterX1=askX.fetch_balance()
    afterX2=bidX.fetch_balance()
    profit={}
    for s in ["USD", "BCH", "LTC"]:
       profit[s]="{:02.6f}".format(afterX1['total'][s]+afterX2['total'][s]-beforeX1['total'][s]-beforeX2['total'][s])
    print("Before: ",beforeX1['total'], beforeX2['total'])
    print("After:  ",afterX1['total'], afterX2['total'])
    print(profit)
    sys.exit()

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
    with open('apiKeys', 'r') as f:
        args = json.load(f)
    t=0
    while 1:
        job(args)
        #schedule.run_pending()
        time.sleep(60)


