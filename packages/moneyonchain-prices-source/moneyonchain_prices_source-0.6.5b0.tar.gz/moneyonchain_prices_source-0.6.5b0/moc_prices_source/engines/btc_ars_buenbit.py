from engine_base import Base, BTC_ARS
from decimal import Decimal


class Engine(Base):

    _name        = Base._name_from_file(__file__)
    _description = "BuenBit"
    _uri         = "https://be.buenbit.com/api/market/tickers"
    _coinpair    = BTC_ARS
    
    _max_age                       = 3600 # 1hs.
    _max_time_without_price_change = 0    # zero means infinity

    def _map(self, data):
        value = {}
        i = data['object']['btcars']
        value['price'] = (Decimal(i['selling_price']) + Decimal(i['purchase_price'])) / Decimal('2')
        return value


if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
    engine = Engine()
    engine()
    print(engine)
    if engine.error:
        print(engine.error)
