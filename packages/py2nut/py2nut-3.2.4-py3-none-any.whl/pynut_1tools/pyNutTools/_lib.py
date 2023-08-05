#-----------------------------------------------------------------
# Generic Lib
#-----------------------------------------------------------------
def logging():
    try:    import logging
    except Exception as err:
        print('  IMPORT FAIL |logging|, err:|{}|'.format(err))
        return None
    return logging

def logger():
    try:
        import logging
        logger = logging.getLogger()
    except Exception as err:
        print('  IMPORT FAIL |logger|, err:|{}|'.format(err))
        return None
    return logger


#-----------------------------------------------------------------
# dataframe
#-----------------------------------------------------------------
def numpy():
    try:    import numpy
    except Exception as err:
        print('  IMPORT FAIL |numpy|, err:|{}|'.format(err))
        return None
    return numpy

def pandas():
    try:    import pandas
    except Exception as err:
        print('  IMPORT FAIL |pandas|, err:|{}|'.format(err))
        return None
    return pandas


#-----------------------------------------------------------------
# Date
#-----------------------------------------------------------------
def dateutil():
    try:    import dateutil
    except Exception as err:
        print('  IMPORT FAIL |dateutil|, err:|{}|'.format(err))
        return None
    return dateutil

def BDay():
    try:    from pandas.tseries.offsets import BDay
    except Exception as err:
        print('  IMPORT FAIL |BDay|, err:|{}|'.format(err))
        return None
    return BDay

def relativedelta():
    try:    from dateutil.relativedelta import relativedelta
    except Exception as err:
        print('  IMPORT FAIL |relativedelta|, err:|{}|'.format(err))
        return None
    return relativedelta

def dateutil_parse():
    try:    from dateutil.parser import parse as dateutil_parse
    except  Exception as err:
        print('  IMPORT FAIL |dateutil_parse|, err:|{}|'.format(err))
        return None
    return dateutil_parse
