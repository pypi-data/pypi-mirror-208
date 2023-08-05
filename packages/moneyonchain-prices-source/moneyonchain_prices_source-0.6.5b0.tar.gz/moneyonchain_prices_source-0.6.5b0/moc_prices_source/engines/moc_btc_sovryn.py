from engine_base import BaseOnChain, MOC_BTC



class Engine(BaseOnChain):

    _name          = BaseOnChain._name_from_file(__file__)
    _description   = "Sovryn onchain"
    _coinpair      = MOC_BTC
    _uri           = 'https://public-node.rsk.co'
    _pool_sc_addr  = '0xe321442dc4793c17f41fe3fb192a856a4864ceaf'
    _wrbtc_tk_addr = '0x542fda317318ebf1d3deaf76e0b632741a7e677d'
    _moc_tk_addr   = '0x9ac7fe28967b30e3a4e6e03286d715b42b453d10'

    def _get_price(self):

        try:
            
            pool_sc_addr = self.Web3.toChecksumAddress(self._pool_sc_addr)
            wrbtc_tk_addr = self.Web3.toChecksumAddress(self._wrbtc_tk_addr)
            moc_tk_addr = self.Web3.toChecksumAddress(self._moc_tk_addr)

            w3 = self.Web3(self.HTTPProvider(self._uri))

            moc_token = w3.eth.contract(address=moc_tk_addr, abi=self.erc20_simplified_abi)
            wrbtc_token = w3.eth.contract(address=wrbtc_tk_addr, abi=self.erc20_simplified_abi)

            moc_reserve = moc_token.functions.balanceOf(pool_sc_addr).call()
            btc_reserve = wrbtc_token.functions.balanceOf(pool_sc_addr).call()

            return btc_reserve/moc_reserve

        except Exception as e:
            self._error = str(e)
            return None





if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
    engine = Engine()
    engine()
    if engine.error:
        print(f"{engine} Error: {engine.error}")
    else:
        print(engine)
