from engine_base import Base, BTC_USD


class Engine(Base):

    _name        = Base._name_from_file(__file__)
    _description = "Gemini"
    _uri         = "https://api.gemini.com/v1/pubticker/BTCUSD"
    _coinpair    = BTC_USD

    def _map(self, data):
        return {
            'price':  data['last'],
            }


if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
    engine = Engine()
    engine()
    print(engine)
