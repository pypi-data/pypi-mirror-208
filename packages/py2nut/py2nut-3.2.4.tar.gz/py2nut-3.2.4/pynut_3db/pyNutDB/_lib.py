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
            print('  Import FAIL PyNutDb |nutOther|, err:|{}|'.format(err))
            return None
    return nutOther

def nutFiles():
    try:
        from pynut_2files.pyNutFiles import nutFiles
    except:
        try:
            from pyNutFiles import nutFiles
        except Exception as err:
            print('  Import FAIL PyNutDb |nutFiles|, err:|{}|'.format(err))
            return None
    return nutFiles



#-----------------------------------------------------------------
# Generic Lib
#-----------------------------------------------------------------
def logging():
    try:    import logging
    except Exception as err:
        print('  Import Fail PyNutDb |logging|, err:|{}|'.format(err))
        return None
    return logging

def logger():
    try:
        import logging
        logger = logging.getLogger()
    except Exception as err:
        print('  Import Fail PyNutDb |logger|, err:|{}|'.format(err))
        return None
    return logger


#-----------------------------------------------------------------
# dataframe
#-----------------------------------------------------------------
def numpy():
    try:    import numpy
    except Exception as err:
        print('  Import Fail PyNutDb |numpy|, err:|{}|'.format(err))
        return None
    return numpy

def pandas():
    try:    import pandas
    except Exception as err:
        print('  Import Fail PyNutDb |pandas|, err:|{}|'.format(err))
        return None
    return pandas


#-----------------------------------------------------------------
# DB
#-----------------------------------------------------------------
def pyodbc():
    try:    import pyodbc
    except Exception as err:
        print('  Import Fail PyNutDb |pyodbc|, err:|{}|'.format(err))
        return None
    return pyodbc

def sqlite3():
    try:    import sqlite3
    except Exception as err:
        print('  Import Fail PyNutDb |sqlite3|, err:|{}|'.format(err))
        return None
    return sqlite3

# def sqlalchemy():
#     try:    import sqlalchemy
#     except Exception as err:
#         print('  Import Fail PyNutDb |sqlalchemy|, err:|{}|'.format(err))
#         return None
#     return sqlalchemy

