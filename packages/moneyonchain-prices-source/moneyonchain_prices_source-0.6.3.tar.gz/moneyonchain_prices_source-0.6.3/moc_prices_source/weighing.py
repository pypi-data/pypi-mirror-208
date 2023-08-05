import datetime, requests
from os.path      import dirname, abspath
from json         import load, dumps
from json.decoder import JSONDecodeError
from sys          import stderr
from statistics   import median, mean
from tabulate     import tabulate
from decimal      import Decimal



filename = dirname(abspath(__file__)) + '/data/weighing.json'
url      = None # 'https://api.moneyonchain.com/static/archive/moc_prices_source/weighing.json'


def get_json_file():

    def config_error(e, source):
        s = "Config file error\nLocation: {}\n{}"
        print(s.format(source, e), file=stderr)
        exit(1)

    def validate_json_data(data):       
        if not isinstance(data, dict):
            return False
        for key, value in data.items():
            if isinstance(value, int):
                data[key]=float(value)
        for key, value in data.items():
            if not isinstance(key, str):
                return False
            if not isinstance(value, float):
                return False
        return True

    try:
        with open(filename) as json_file:
            data = load(json_file)
    except JSONDecodeError as e:
        config_error(e, filename)
    except FileNotFoundError as e:
        config_error('File not found!', filename)

    if not validate_json_data(data):
        str_err_map = "Bad mapping, has to be a dictionary with string keys and float values"
        config_error(str_err_map, filename)
    
    if url:
        try:
            new_data = requests.get(url).json()
        except:
            new_data = None
        if new_data and validate_json_data(new_data):
            data = new_data  

    return data



class Weighing(object):

    def __init__(self, refresh_time=datetime.timedelta(minutes=60)):
        self._data = {}
        self._last_load = None
        self._refresh_time = refresh_time
        self._load()

    def _load(self):

        if ((self._last_load is None) or (
            (datetime.datetime.now() - self._last_load) > self._refresh_time)):

            data = get_json_file()

            if isinstance(data, dict):
                ok = True
                try:
                    for key, value in data.items():
                        data[key] = Decimal(str(value))
                except:
                    ok = False

                if ok:
                    for key, value in data.items():
                        self._data[key] = value
                    self._last_load = datetime.datetime.now()

    @property
    def as_dict(self):
        self._load()
        return dict(self._data)

    @property
    def names(self):
        return list(self.as_dict.keys())

    def __call__(self, name):
        return  self.as_dict.get(name, Decimal('0.0'))

    @property
    def last_load(self):
        return self._last_load

    @property
    def refresh_time(self):
        return self._refresh_time

    def __str__(self):
        return tabulate(list(self.as_dict.items()),
            headers=['Engine', 'Weigh'])



weighing = Weighing()



def weighted_median(values, weights):
    idx = weighted_median_idx(values, weights)
    return values[idx]


def weighted_median_idx(values, weights):
    ''' compute the weighted median of values list. The weighted median is computed as follows:
    1- sort both lists (values and weights) based on values.
    2- select the 0.5 point from the weights and return the corresponding values as results
    e.g. values = [1, 3, 0] and weights=[0.1, 0.3, 0.6] assuming weights are probabilities.
    sorted values = [0, 1, 3] and corresponding sorted weights = [0.6,     0.1, 0.3] the 0.5 point on
    weight corresponds to the first item which is 0. so the weighted     median is 0.'''

    # convert the weights into probabilities
    sum_weights = sum(weights)
    weights = [w / sum_weights for w in weights]
    # sort values and weights based on values
    sorted_tuples = sorted(zip(values, weights, range(len(values))))

    # select the median point
    cumulative_probability = 0
    for i in range(len(sorted_tuples)):
        cumulative_probability += sorted_tuples[i][1]
        if cumulative_probability > 0.5:
            return sorted_tuples[i][2]
        elif cumulative_probability == 0.5:
            # if i + 1 >= len(sorted_tuples):
            return sorted_tuples[i][2]
            # return (sorted_tuples[i][2] + sorted_tuples[i + 1][2]) / 2
    return sorted_tuples[-1][2]



if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
    print("Config file: {}".format(repr(filename)))
    print()
    print('weighing.as_dict = {}'.format(repr(weighing.as_dict)))
    print()
    print(weighing)
    print()
