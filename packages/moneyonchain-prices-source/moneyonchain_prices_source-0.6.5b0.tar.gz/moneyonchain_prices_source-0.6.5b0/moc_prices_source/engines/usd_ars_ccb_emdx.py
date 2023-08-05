from engine_base import Base, USD_ARS_CCB
from decimal     import Decimal


class Engine(Base):

    _name        = Base._name_from_file(__file__)
    _description = "emdx.io"
    _uri         = "https://api.emdx.io/api/v1/markets/full?chainId=43114"
    _headers     = {"origin": "https://app.emdx.io"} # without this it gives: 500 Server Error   
    _coinpair    = USD_ARS_CCB

    _max_age                       = 3600 # 1hs.
    _max_time_without_price_change = 0    # zero means infinity

    def _map(self, data):
        value = None
        for item in data['data']['results']:
            if item['symbol']=='ars/usdc':
                value = Decimal(item['data24hs']['last24hs'])
                break
        return {
            'price':  value
        }


if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
    engine = Engine()
    engine()
    print(engine)
    if engine.error:
        print(engine.error)
