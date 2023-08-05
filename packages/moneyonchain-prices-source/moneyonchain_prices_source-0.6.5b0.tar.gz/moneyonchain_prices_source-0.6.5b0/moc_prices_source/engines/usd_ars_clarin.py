from engine_base import Base, USD_ARS
from decimal     import Decimal


class Engine(Base):

    _name        = Base._name_from_file(__file__)
    _description = "Clarin.com"
    _uri         = "https://www.clarin.com/economia/divisas-acciones-bonos/monedas.json"
    _coinpair    = USD_ARS

    _max_age                       = 3600 # 1hs.
    _max_time_without_price_change = 0    # zero means infinity

    def _map(self, data):
        value = None
        for i in data:
            if 'nombre' in i and i['papel']=="DLRBLE":
                values = [i['ultimoval'], i['compraval']]
                values = list(map(lambda x: Decimal(str(x).replace(',', '')), values))
                value = sum(values)/len(values)
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
