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
            print('  Import FAIL PyNutEmail |nutOther|, err:|{}|'.format(err))
            return None
    return nutOther

def nutDate():
    try:
        from pynut_1tools.pyNutTools import nutDate
    except:
        try:
            from pyNutTools import nutDate
        except Exception as err:
            print('  Import FAIL PyNutEmail |nutDate|, err:|{}|'.format(err))
            return None
    return nutDate

def nutFiles():
    try:
        from pynut_2files.pyNutFiles import nutFiles
    except:
        try:
            from pyNutFiles import nutFiles
        except Exception as err:
            print('  Import FAIL PyNutEmail |nutFiles|, err:|{}|'.format(err))
            return None
    return nutFiles



#-----------------------------------------------------------------
# Generic Lib
#-----------------------------------------------------------------
def logging():
    try:    import logging
    except Exception as err:
        print('  Import Fail PyNutEmail |logging|, err:|{}|'.format(err))
        return None
    return logging

def logger():
    try:
        import logging
        logger = logging.getLogger()
    except Exception as err:
        print('  Import Fail PyNutEmail |logger|, err:|{}|'.format(err))
        return None
    return logger

def win32():
    try:    import win32com.client as win32
    except Exception as err:
        print('  Import Fail PyNutEmail |win32|, err:|{}|'.format(err))
        return None
    return win32

def pythoncom():
    try:    import pythoncom
    except Exception as err:
        print('  Import Fail PyNutEmail |pythoncom|, err:|{}|'.format(err))
        return None
    return pythoncom


#-----------------------------------------------------------------
# dataframe
#-----------------------------------------------------------------
def numpy():
    try:    import numpy
    except Exception as err:
        print('  Import Fail PyNutEmail |numpy|, err:|{}|'.format(err))
        return None
    return numpy

def pandas():
    try:    import pandas
    except Exception as err:
        print('  Import Fail PyNutEmail |pandas|, err:|{}|'.format(err))
        return None
    return pandas


#-----------------------------------------------------------------
# EMAIL
#-----------------------------------------------------------------
def Credentials():
    try:    from exchangelib import Credentials
    except Exception as err:
        print('  Import Fail PyNutEmail |Credentials|, err:|{}|'.format(err))
        return None
    return Credentials

def Account():
    try:    from exchangelib import Account
    except Exception as err:
        print('  Import Fail PyNutEmail |Account|, err:|{}|'.format(err))
        return None
    return Account

def Configuration():
    try:    from exchangelib import Configuration
    except Exception as err:
        print('  Import Fail PyNutEmail |Configuration|, err:|{}|'.format(err))
        return None
    return Configuration

def DELEGATE():
    try:    from exchangelib import DELEGATE
    except Exception as err:
        print('  Import Fail PyNutEmail |DELEGATE|, err:|{}|'.format(err))
        return None
    return DELEGATE

def FileAttachment():
    try:    from exchangelib import FileAttachment
    except Exception as err:
        print('  Import Fail PyNutEmail |FileAttachment|, err:|{}|'.format(err))
        return None
    return FileAttachment

def EWSTimeZone():
    try:    from exchangelib import EWSTimeZone
    except Exception as err:
        print('  Import Fail PyNutEmail |EWSTimeZone|, err:|{}|'.format(err))
        return None
    return EWSTimeZone

def EWSDateTime():
    try:    from exchangelib import EWSDateTime
    except Exception as err:
        print('  Import Fail PyNutEmail |EWSDateTime|, err:|{}|'.format(err))
        return None
    return EWSDateTime
