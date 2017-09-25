import pickle

token = '445186548:AAGPAHB7eDP7eXoEe3Zoxqc1uFvTsRahDbU'


def quote(s):
    return '\'{}\''.format(s)


def quote2(s):
    return '\"{}\"'.format(s)


def load_config():
    with open('aws-rds-params.pickle', 'rb') as cfg_file:
        config = pickle.load(cfg_file)
    return config

def crate_query_text(info:dict):
    columns, values_len = "", ""
    values = list()
    for i, (key, value) in enumerate(info.items()):
        columns += ('\"' + key + '\",')
        values_len += ('$' + str(i + 1) + ',')
        values.append(value)
    return columns[:-1],values_len[:-1],values

def prepared(n):
    return ['$' + str(k) for k in range(1, n + 1)]
