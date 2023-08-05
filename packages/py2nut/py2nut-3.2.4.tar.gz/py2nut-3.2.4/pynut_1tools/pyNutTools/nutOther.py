try:
    from pynut_1tools.pyNutTools import _lib as lib
except:
    try:
        from pyNutTools import _lib as lib
    except:
        try:
            from . import _lib as lib
        except:
            import _lib as lib

logger = lib.logger()
import sys
import time
import collections
import threading
import json
import warnings



#------------------------------------------------------------------------------
# Specific Message
#------------------------------------------------------------------------------
def DisplayMessage_Python3():
    logger.error('  ERROR: You must use Python 3 to use this App')

def fStr_PythonVersion():
    str_PythonList = sys.version
    # 3.7.0 (default, Jun 29 2018, 20:13:13)
    try:
        str_versionPython = str_PythonList.split('(')[0]
        # print(str_versionPython)
    except:
        return str_PythonList

    # print(sys.version_info)
    # sys.version_info(major=3, minor=7, micro=0, releaselevel='final', serial=0)

    # import platform
    # print(platform.python_version())
    # # 3.7.0
    return str_versionPython



#---------------------------------------------------------------
# Decorator
#---------------------------------------------------------------
def dec_TempSuppressWarnings(type = DeprecationWarning):
    ''' This Decorator allows to avoid displaying Deprecation Warning
    (or other warnings) for the time of the function
    '''
    def dec_decoratorinside(input_fct):
        def wrap_modifiedFunction(*l_paramInput, **d_paramInput):
            #------- Before Function Execution -------
            with warnings.catch_warnings(record=True):
                warnings.simplefilter("always")
                # warnings.simplefilter("ignore")
                #------- Function execution -------
                launchFunction = input_fct(*l_paramInput, **d_paramInput)
                #------- After Function Execution -------
                warnings.resetwarnings()
            #------- Return the Function at the end-------
            return launchFunction
        return wrap_modifiedFunction
    return dec_decoratorinside

def dec_singletonsClass(input_classe):
    '''
    Singeltons decorators: always use the first instance
    exemple : instance of db connexion , we do not want several instances but always the first one if existing
    '''    
    d_instances = {}
    def wrap_getInstances(*l_paramInput, **d_paramInput):
        if input_classe not in d_instances:
            # Add instances as value in the dictionary where the key is the class
            d_instances[input_classe] = input_classe(*l_paramInput, **d_paramInput)
        # If an instance already exist for ones class, just use this instance
        return d_instances[input_classe]
    return wrap_getInstances

def dec_getTimePerf(int_secondesLimitDisplay = 1):
    '''
    Time Performance Decorators on a function
    You can calculate and compare Performance on any function just by decorating it
    You nest decorator within another to be able to add an Argument
     - here, i dont want to display the performance if its quick enough ! 
    '''    
    def dec_decoratorinside(input_fct):
        def wrap_modifiedFunction(*l_paramInput, **d_paramInput):
            # Before Function Execution...
            time_Debut = time.time()
            # Function execution 
            launchFunction = input_fct(*l_paramInput, **d_paramInput)
            # After Function Execution...
            time_Fin = time.time()
            time_duree = time_Fin - time_Debut
            sec_duree = int(time_duree)
            milli_duree = int((time_duree - sec_duree) * 1000)
            if sec_duree >= int_secondesLimitDisplay:
                logger.warning(' * Execution time: {} = {} sec, {} milliSec \n'.format(input_fct, sec_duree, milli_duree))
                # prrint(' * Execution time: {} = {} sec, {} milliSec \n'.format(input_fct, sec_duree, milli_duree))
            # Return the Function at the end
            return launchFunction
        return wrap_modifiedFunction
    return dec_decoratorinside

def dec_stopProcessTimeOut(int_secondesLimit = 5, returnIfTimeOut = None):
    '''
    This decorators allow to stop a process if it is too long
    For example, testing a folder existence might be very very long...
    '''
    def dec_decoratorinside(input_fct):
        def wrap_modifiedFunction(*l_paramInput, **d_paramInput):
            procss = InterruptableThread(input_fct, *l_paramInput, **d_paramInput)
            procss.start()
            procss.join(int_secondesLimit)
            if procss.is_alive():
                logger.warning('  Function is TIMEOUT: |{}|'.format(input_fct.__name__))
                return returnIfTimeOut
            else:
                return procss.result
        return wrap_modifiedFunction
    return dec_decoratorinside



#-----------------------------------------------------------------
# Threading
#-----------------------------------------------------------------
class InterruptableThread(threading.Thread):
    def __init__(self, func, *args, **kwargs):
        threading.Thread.__init__(self)
        self._func = func
        self._args = args
        self._kwargs = kwargs
        self._result = None

    def run(self):
        self._result = self._func(*self._args, **self._kwargs)

    @property
    def result(self):
        return self._result



#-----------------------------------------------------------------
# String
#-----------------------------------------------------------------
def fStr_RemoveDicoBracket(str_in):
    # Remove the first and last Char if its {}
    try:
        if str_in[0] == '{':    str_in = str_in[1:]
        if str_in[-1] == '}':   str_in = str_in[:-1]
    except Exception as err:
        logger.error(' ERROR fStr_RemoveDicoBracket ||| {}'.format(err))
        logger.error(' - str_in: {}'.format(str_in))
    return str_in

def fStr_CleanStringFromSymbol(str_in):
    str_in = str_in.replace("'", "").replace(" ", "")
    str_in = str_in.replace("[", "").replace("]", "")
    str_in = str_in.replace("{", "").replace("}", "")
    str_in = str_in.replace("\n", "")
    return str_in

def fInt_convertStrCalendar(str_CalendarID):
    try:
        if type(str_CalendarID) == str:
            str_CalendarID =    str_CalendarID.replace('.0', '')
            str_CalendarID =    str_CalendarID.replace(' ', '')
            if str_CalendarID == '':
                int_CalendarID = 0
            else:
                int_CalendarID = int(str_CalendarID)
        else:
            int_CalendarID = int(str_CalendarID)
    except Exception as err:
        logger.error(' ERROR in fInt_convertStrCalendar: |{}|'.format(err))
        raise
    return int_CalendarID



#-----------------------------------------------------------------
# List
#-----------------------------------------------------------------
def fL_GetFlatList_fromListOfList(ll_input):
    l_list = [x for l_subList in ll_input for x in l_subList]
    return l_list



#-----------------------------------------------------------------
# Dictionary
#-----------------------------------------------------------------
def fDic_comprehension(original_dict):
    new_dict = {num: num*num for num in range(1, 11)}
    new_dict = {k: v * 2 for(k, v) in original_dict.items()}
    new_dict = {k: v for (k, v) in original_dict.items() if v % 2 == 0}
    new_dict = {k: v for (k, v) in original_dict.items() if v % 2 != 0 if v < 40}
    return new_dict

def fDic_mergeDico(d_first, d_update):
    d_dico = {**d_first, **d_update}
    return d_dico

def fDic_deepUpdateDico(dic_original, dic_update):
    for k, v in dic_update.items():
        # this condition handles the problem
        if not isinstance(dic_original, collections.abc.Mapping):
            dic_original = dic_update
        elif isinstance(v, collections.abc.Mapping):
            r = fDic_deepUpdateDico(dic_original.get(k, {}), v)
            dic_original[k] = r
        else:
            dic_original[k] = dic_update[k]
    return dic_original

def fDic_GetDicFromString(str_in, str_valueType = 'list'):
    d_dico = eval(str_in)
    return d_dico

def fDic_GetStrFromDic(d_in):
    str_json = json.dumps(d_in)
    return str_json

    


#---------------------------------------------------------------
# Log and prrint
#---------------------------------------------------------------
def fStr_Message(str_in):
    logger.warning(str_in)
    return '\n' + str_in

