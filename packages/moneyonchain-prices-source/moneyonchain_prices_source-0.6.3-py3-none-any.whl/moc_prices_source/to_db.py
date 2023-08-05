import sys, datetime
from os.path  import dirname, abspath
from time     import sleep
from tabulate import tabulate

bkpath   = sys.path[:]
base_dir = dirname(abspath(__file__))
sys.path.append(dirname(base_dir))

from moc_prices_source            import get_price
from moc_prices_source            import ALL
from moc_prices_source.cli        import command, option
from moc_prices_source.database   import database, database_error_message
from moc_prices_source.my_logging import make_log, INFO, DEBUG, VERBOSE

sys.path = bkpath
app_name = 'moc_prices_source'



class OutputClose(Exception):
    pass



class OutputBase(object):

    def __init__(self, name,
                 verbose  = print,
                 critical = lambda m: print(m, file=sys.stderr)):
        self._verbose  = verbose
        self._critical = critical
        self._name = name
        self._open = False
        self._start()
        self._open = True

    @property
    def name(self):
        return self._name
    
    def __bool__(self):
        return self._open

    def __call__(self, value):
        if self:
            return self._call(value)
        else:
            raise OutputClose()

    def close(self):
        if self:
            self._end()
            self._open = False

    def __del__(self):
        self.close()

    def _start(self):
        pass

    def _call(self, value):
        pass

    def _end(self):
        pass



class OutputDB(OutputBase):

    def _start(self):
        if not database:
            for l in database_error_message.split('\n'):
                if l:
                    self._critical(l)
            exit(1)

    def _call(self, value):
        data = {}
        for timestamp, name, v in value:
            if not timestamp in data:
                data[timestamp] = {}
            data[timestamp][name] = v
        timestamps = list(data.keys())
        timestamps.sort(key=lambda x: x.timestamp())
        for timestamp in timestamps:
            kargs = {
                'measurement': self.name,
                'time_':       timestamp,
                'fields':      data[timestamp]
            }
            database.write(**kargs)



def get_values(log):

    # Get prices
    d = {}
    get_price(ALL, detail=d)

    # Log errors
    for e in d['prices']:
        if not(e['ok']):
            coinpair = e['coinpair']
            exchange = e['description']
            error    = e['error']
            log.warning(f'{exchange} {coinpair} {error}')

    data = []

    for p in d['prices']:
        timestamp = p['timestamp'] if p['timestamp'] else datetime.datetime.now().replace(microsecond=0)
        coinpair =  p['coinpair']
        name =      p['description']
        price =     p['price']
        weighing =  None if p['percentual_weighing'] is None else float(p['percentual_weighing'])
        age =       None if p['age'] is None else int(p['age'])
        error =     None if p['error'] is None else str(p['error'])
        row = {
            'timestamp':            timestamp,
            'coinpair':             coinpair,
            'name':                 name,
            'price':                price,
            'percentual_weighing':  weighing,
            'age': age,
            'error': error
        }
        log.verbose(f'Exchange {name} {coinpair} value: {price}')
        data.append(row)

    for coinpair, v in d['values'].items():
        median_price =          v['median_price']
        mean_price =            v['mean_price']
        weighted_median_price = v['weighted_median_price']
        row = {
            'timestamp':             datetime.datetime.now().replace(microsecond=0),
            'coinpair':              coinpair,
            'median_price':          median_price,
            'mean_price':            mean_price,
            'weighted_median_price': weighted_median_price
        }
        log.info(f'{coinpair} weighted:{weighted_median_price}, median;{median_price}, mean:{mean_price}')
        data.append(row)

    out = []

    for d in data:

        timestamp = d['timestamp']

        pre_name = str(d['coinpair']).split('/')
        if 'name' in d:
            pre_name += d['name'].split()
        pre_name += ['']
        pre_name = '_'.join(pre_name)

        for k in [k for k in d.keys() if k not in ['name', 'coinpair', 'timestamp']]:
            row = [timestamp, pre_name + k, d[k]] 
            out.append(row)

    out.sort(key=lambda x: x[0].timestamp())
    return out



@command()
@option('-v', '--verbose', 'verbose', count=True,
    help='Verbose mode.')
@option('-f', '--frequency', 'frequency', type=int, default=5,
    help='Loop delay in seconds.')
@option('-i', '--interval', 'interval', type=int, default=0,
    help='How long the program runs (in minutes, 0 = infinity)')
def cli_values_to_db(frequency, verbose=0, interval=0):
    """ MoC prices source to DB """

    # Logger
    if verbose==0:
        level = INFO
    elif verbose==1:
        level = VERBOSE
    elif verbose>1:
        level = DEBUG
    log = make_log(app_name, level = level)
    log.info(f'Starts (frequency {frequency}s)')

    output = OutputDB(app_name, verbose=log.verbose, critical=log.critical)

    start_time = datetime.datetime.now()

    def condition():
        if not interval:
            return True
        until_now = datetime.datetime.now() - start_time
        return until_now <= datetime.timedelta(minutes=interval)

    try:
        while condition():
            output(get_values(log))
            sleep(frequency)
    except KeyboardInterrupt:
        log.verbose('Keyboard interrupt!')
        print()
        print('Aborted!')
        print()

    if not condition():
        log.info(f'Ends (interval {interval}m)')        



if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
    log = make_log(app_name, level = INFO)
    values = get_values(log)
    print()
    print(tabulate(values, headers=['timestamp', 'key', 'value']))
    print()