#-----------------------------------------------------------------
# pynut
#-----------------------------------------------------------------
def nutOther():
    try:
        from pynut_1tools.pyNutTools import nutOther
    except:
        try:
            from pyNutTools import nutOther
        except Exception as err:
            print('  Import FAIL PyNutApi |nutOther|, err:|{}|'.format(err))
            return None
    return nutOther

def nutDataframe():
    try:
        from pynut_1tools.pyNutTools import nutDataframe
    except:
        try:
            from pyNutTools import nutDataframe
        except Exception as err:
            print('  Import FAIL PyNutApi |nutDataframe|, err:|{}|'.format(err))
            return None
    return nutDataframe


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
# API
#-----------------------------------------------------------------
def re():
    try:    import re
    except Exception as err:
        print('  IMPORT FAIL |re|, err:|{}|'.format(err))
        return None
    return re

def requests():
    try:    import requests
    except Exception as err:
        print('  IMPORT FAIL |requests|, err:|{}|'.format(err))
        return None
    return requests

def BeautifulSoup():
    try:    from bs4 import BeautifulSoup
    except Exception as err:
        print('  IMPORT FAIL |BeautifulSoup|, err:|{}|'.format(err))
        return None
    return BeautifulSoup

def urlopen():
    try:    from urllib.request import urlopen
    except Exception as err:
        print('  IMPORT FAIL |urlopen|, err:|{}|'.format(err))
        return None
    return urlopen

def urlretrieve():
    try:    from urllib.request import urlretrieve
    except Exception as err:
        print('  IMPORT FAIL |urlretrieve|, err:|{}|'.format(err))
        return None
    return urlretrieve

def unicodedata():
    try:    import unicodedata
    except Exception as err:
        print('  IMPORT FAIL |unicodedata|, err:|{}|'.format(err))
        return None
    return unicodedata

def selenium():
    try:    import selenium
    except Exception as err:
        print('  IMPORT FAIL |selenium|, err:|{}|'.format(err))
        return None
    return selenium

def selenium_webdriver():
    try:    from selenium import webdriver as selenium_webdriver
    except Exception as err:
        print('  IMPORT FAIL |selenium_webdriver|, err:|{}|'.format(err))
        return None
    return selenium_webdriver


