from engine_base import Base, ETH_BTC


class Engine(Base):

    _name        = Base._name_from_file(__file__)
    _description = "Binance"
    _uri         = "https://api.binance.com/api/v3/ticker/24hr?symbol=ETHBTC"
    _coinpair    = ETH_BTC

    def _map(self, data):
        return {
            'price':  data['lastPrice'],
            'volume': data['volume']}


if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
    engine = Engine()
    engine()
    print(engine)
    if engine.error:
        print(engine.error)
