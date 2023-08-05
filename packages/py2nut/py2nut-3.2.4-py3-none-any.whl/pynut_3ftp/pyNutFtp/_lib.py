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
            print('  Import FAIL pyNutFtp |nutOther|, err:|{}|'.format(err))
            return None
    return nutOther

def nutDate():
    try:
        from pynut_1tools.pyNutTools import nutDate
    except:
        try:
            from pyNutTools import nutDate
        except Exception as err:
            print('  Import FAIL pyNutFtp |nutDate|, err:|{}|'.format(err))
            return None
    return nutDate

def nutFiles():
    try:
        from pynut_2files.pyNutFiles import nutFiles
    except:
        try:
            from pyNutFiles import nutFiles
        except Exception as err:
            print('  Import FAIL pyNutFtp |nutFiles|, err:|{}|'.format(err))
            return None
    return nutFiles




#-----------------------------------------------------------------
# Generic Lib
#-----------------------------------------------------------------
def logging():
    try:    import logging
    except Exception as err:
        print('  Import FAIL pyNutFtp |logging|, err:|{}|'.format(err))
        return None
    return logging

def logger():
    try:
        import logging
        logger = logging.getLogger()
    except Exception as err:
        print('  Import FAIL pyNutFtp |logger|, err:|{}|'.format(err))
        return None
    return logger

def fnmatch():
    try:    import fnmatch
    except Exception as err:
        print('  Import FAIL pyNutFtp |fnmatch|, err:|{}|'.format(err))
        return None
    return fnmatch

def warnings():
    try:    import warnings
    except Exception as err:
        print('  Import FAIL pyNutFtp |warnings|, err:|{}|'.format(err))
        return None
    return warnings


#-----------------------------------------------------------------
# FTP
#-----------------------------------------------------------------
def ftplib():
    try:    import ftplib
    except Exception as err:
        print('  Import FAIL pyNutFtp |ftplib|, err:|{}|'.format(err))
        return None
    return ftplib

def SSLSocket():
    try:    from ssl import SSLSocket
    except Exception as err:
        print('  Import FAIL pyNutFtp |SSLSocket|, err:|{}|'.format(err))
        return None
    return SSLSocket

def paramiko():
    try:    import paramiko
    except Exception as err:
        print('  Import FAIL pyNutFtp |paramiko|, err:|{}|'.format(err))
        return None
    return paramiko

def pysftp():
    try:    import pysftp
    except Exception as err:
        print('  Import FAIL pyNutFtp |pysftp|, err:|{}|'.format(err))
        return None
    return pysftp


#-----------------------------------------------------------------
# dataframe
#-----------------------------------------------------------------
def numpy():
    try:    import numpy
    except Exception as err:
        print('  Import FAIL pyNutFtp |numpy|, err:|{}|'.format(err))
        return None
    return numpy

def pandas():
    try:    import pandas
    except Exception as err:
        print('  Import FAIL pyNutFtp |pandas|, err:|{}|'.format(err))
        return None
    return pandas
