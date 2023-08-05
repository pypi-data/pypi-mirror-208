from engine_base import EngineWebScraping, USD_ARS_CCL
from decimal     import Decimal


class Engine(EngineWebScraping):

    _name        = EngineWebScraping._name_from_file(__file__)
    _description = "Infobae"
    _uri         = "https://www.infobae.com/economia/divisas/dolar-hoy/"
    _coinpair    = USD_ARS_CCL

    _max_age                       = 3600 # 1hs.
    _max_time_without_price_change = 0    # zero means infinity

    def _scraping(self, html):
        value = None
        for s in html.find_all ('p', attrs={'class':'exc-tit'}):
            d = list(map(lambda x: x.strip(), s.parent.strings))
            if len(d)==2 and d[0]=='Contado con liqui':
                try:
                    value = Decimal(d[1])
                except:
                    value = None
                if value:
                    break
        if not value:
            self._error = "Response format error"
            return None
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
