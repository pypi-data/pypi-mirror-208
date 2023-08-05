from engine_base import Base, BNB_USDT


class Engine(Base):

    _name        = Base._name_from_file(__file__)
    _description = "Binance"
    _uri         = "https://api.binance.com/api/v3/ticker/24hr?symbol=BNBUSDT"
    _coinpair    = BNB_USDT

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
