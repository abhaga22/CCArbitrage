#logic
#For each symbol pair
# for each exchange
#  fetch symbol price
# l = get lowest ask price
# h = get highest bid price
# if h > l*1.005
# raise warning
import ccxt
import schedule, time

def job():
##symbols = ['BCH/USD', 'ETH/USD', 'LTC/USD', 'DASH/USD']
    symbols = ['BCH/USD', 'LTC/USD', 'ETH/USD']
    pairs = [(r,s) for s in symbols for r in symbols if r is not s]
    gdax = ccxt.gdax({'password':'', 'apiKey':'', 'secret':''})
    gdax.load_markets()
    bitfinex = ccxt.bitfinex({'apiKey':'', 'secret':''})
    bitfinex.load_markets()
    print "Connected to exchanges"
    exchanges = [ gdax, bitfinex ]
    for r, s in pairs:
      print "Fetching values"
      asks, bids={},{}
      for x in exchanges:
        # TODO check if exchange supports symbol
        rPrice=x.fetch_ticker(r)
        sPrice=x.fetch_ticker(s)
        print x.name, rPrice['ask'], rPrice['bid']
        print x.name, sPrice['bid'], sPrice['ask']
        asks[x.name] = rPrice['ask']/rPrice['bid']
        bids[x.name] = sPrice['bid']/sPrice['ask']
      lowX = min(asks, key=asks.get)
      highX = max(bids, key=bids.get)
      print r,s, bids[highX]/asks[lowX]
      if (bids[highX]/asks[lowX]) > 1.005:
        print "CONGRATS you found an opportunity"
        print "Short %s on %s, Long %s on %s" % (s, highX, r, lowX)
      time.sleep(1)

if __name__ == '__main__':
    #schedule.every(1).minutes.do(job)
    while 1:
        job()
        time.sleep(30)
