from engine_base import Base, USD_ARS
from decimal     import Decimal


class Engine(Base):

    _name        = Base._name_from_file(__file__)
    _description = "Dolarito.ar"
    _uri         = "https://www.dolarito.ar/api/frontend/quotations"
    _coinpair    = USD_ARS
    
    _max_age                       = 3600 # 1hs.
    _max_time_without_price_change = 0    # zero means infinity

    def _map(self, data):
        info = data['informal']
        values = [info['buy'], info['sell']]
        values = list(map(lambda x: Decimal(str(x).replace('.', '').replace(',', '.')), values))
        value = sum(values)/len(values)
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
