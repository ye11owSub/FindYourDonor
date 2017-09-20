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


def prepared(n):
    return ['$' + str(k) for k in range(1, n + 1)]
