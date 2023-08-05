


class Coin(object):

    def __init__(self, name: str, symbol: str, small_symbol=None):
        self._name = str(name).strip()
        self._symbol =str(symbol).strip().upper()
        self._small_symbol = str(small_symbol).strip() if small_symbol else None

    @property
    def name(self):
        return self._name

    @property
    def symbol(self):
        return self._symbol

    @property
    def small_symbol(self):
        return self._small_symbol

    def get_symbol(self):
        """ Get small symbol or symbol """
        return self.small_symbol or self.symbol

    @property
    def as_dict(self):
        return {
            'name':         self.name,
            'symbol':       self.symbol,
            'small_symbol': self.small_symbol,
        }

    def __str__(self):
        return self.symbol

    def __repr__(self):
        return "<{} Coin object>".format(self.name)

    def __eq__(self, other):
        return str(self).lower()==str(other).strip().lower()

    def __lt__(self, other):
        return str(self).lower()<str(other).strip().lower()

    def __hash__(self):
        return hash(str(self))


BTC  = Coin('Bitcoin',        'btc',  '₿')
USD  = Coin('Dollar',         'usd',  '$')
RIF  = Coin('RIF Token',      'rif')
ETH  = Coin('Ether',          'eth',  '⟠')
USDT = Coin('Tether',         'usdt', '₮')
BNB  = Coin('Binance Coin',   'bnb',  'Ƀ')
ARS  = Coin('Peso Argentino', 'ars',  '$')
MXN  = Coin('Peso Mexicano',  'mxn',  '$')


Coins = [ c for c in locals().values() if isinstance(c, Coin) ]



def get_coin(value):
    value = str(value).strip().lower()
    try:
        return dict([ (str(c.name).strip().lower(), c) for c in Coins])[value]
    except KeyError:
        return dict([ (str(c).strip().lower(), c) for c in Coins])[value]
        


class CoinPair(object):

    def __init__(self, from_: Coin, to_: Coin, variant=None):
        self._from    = from_
        self._to      = to_
        self._variant = str(variant) if variant else None

    @property
    def variant(self):
        return self._variant

    @property
    def from_(self):
        return self._from

    @property
    def to_(self):
        return self._to

    @property
    def as_dict(self):
        return {
            'from':    self.from_,
            'to':      self.to_,
            'variant': self.variant
        }

    def __str__(self):
        if self.variant:
            return '{}/{}({})'.format(self.from_.symbol, self.to_.symbol, self.variant)
        return '{}/{}'.format(self.from_.symbol, self.to_.symbol)

    def __repr__(self):
        return "<{} Coin Pair object>".format(str(self))

    def __eq__(self, other):
        return str(self).lower()==str(other).strip().lower()

    def __lt__(self, other):
        return str(self).lower()<str(other).strip().lower()

    def __hash__(self):
        return hash(str(self))


BTC_USD         = CoinPair(BTC,  USD)
BTC_ARS         = CoinPair(BTC,  ARS)
RIF_BTC         = CoinPair(RIF,  BTC)
RIF_USD         = CoinPair(RIF,  USD)
ETH_BTC         = CoinPair(ETH,  BTC)
ETH_USD         = CoinPair(ETH,  USD)
BTC_USDT        = CoinPair(BTC,  USDT)
USDT_USD        = CoinPair(USDT, USD)
BNB_USDT        = CoinPair(BNB,  USDT)
BNB_USD         = CoinPair(BNB,  USD)
USD_ARS         = CoinPair(USD,  ARS)
USD_ARS_CCL     = CoinPair(USD,  ARS, "CCL")
USD_ARS_CCB     = CoinPair(USD,  ARS, "CCB")
USD_ARS_CCB_MOC = CoinPair(USD,  ARS, "CCB by MOC")
USD_MXN         = CoinPair(USD,  MXN)


CoinPairs = [ c for c in locals().values() if isinstance(c, CoinPair) ]



def get_coin_pair(value):
    value = str(value).strip().lower()
    return dict([ (str(c).strip().lower(), c) for c in CoinPairs ])[value]



if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
    print()
    print('Coins:')
    for c in Coins:
        if c.small_symbol:
            print(f'    {c.name} ({c.symbol} or {c.small_symbol})')
        else:
            print(f'    {c.name} ({c.symbol})')
    print()
    print('Coin pairs:')
    for c in CoinPairs:
        if c.variant:
            print(f'    {c} (from {c.from_.name} to {c.to_.name}, {c.variant})')
        else:    
            print(f'    {c} (from {c.from_.name} to {c.to_.name})')
