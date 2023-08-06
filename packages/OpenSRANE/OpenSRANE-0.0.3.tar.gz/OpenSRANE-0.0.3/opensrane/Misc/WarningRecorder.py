# /* ****************************************************************** **
# **    OpeSRANE - Open Software for Risk Assessment of Natech Events   **
# **                                                                    **
# **                                                                    **
# **                                                                    **
# ** (C) Copyright 2023, Mentioned Regents in 'COPYRIGHT' file.         **
# **                                                                    **
# ** All Rights Reserved.                                               **
# **                                                                    **
# ** Commercial use of this program without express permission of the   **
# ** owner (The Regents), is                                            **
# ** strictly prohibited.  See file 'COPYRIGHT'  in main directory      **
# ** for information on usage and redistribution,  and for a            **
# ** DISCLAIMER OF ALL WARRANTIES.                                      **
# **                                                                    **
# ** Developed by:                                                      **
# **   Bijan SayyafZadeh (OpenSRANE@Gmail.com)                          **
# **   MehDi Sharifi                                                    **
# **   Abdolreza S. Moghadam                                            **
# **   Eslam Kashi                                                      **
# **                                                                    **
# ** ****************************************************************** */

'''
 Written: Bijan Sayyafzadeh
 Created: 2022
 
 Revision: -
 By & Date: -
'''


import opensrane as _opr
import os as _os
import datetime as _dt
import pickle as _pickle
from copy import deepcopy as _deepcopy
import gc as _gc


class WarningRecorder():
    pass


class _Warnings():
    '''
    This Class specify the Warnings recorder Object and send the Warnings into a input text file
    
    '''
    _PrintedWarning=None
    
    def __init__(self):
    
        self.filename='Warnings.wrn' 
        f = open(self.filename, "w")                            #Every time that an instance made from this file, The content will be deleted
        f.write(f"OpenSRANE - Run at {_dt.datetime.now()} \n")
        f.close()
    
    def __call__(self,string=None):
    
        if string==None:                  #If there is no input data, the object return the whole data of the file
            f = open(self.filename, "r")
            data=f.read()
            f.close()
            return data
            
        
        f = open(self.filename, "a")       #By calling the object, the string in the call will be added to the 'Warnings.wrn' file
        f.write(f'\n {string}')
        f.close()

        if self._PrintedWarning==None:
            self._PrintedWarning=True
            print('*** Check Warning File ***')

def warningClear():
    '''
    This command clear the warning file content and reset the warning object
    Currently By wipe command the warning content does not remove
    '''
    if '_oprwarnobj' not in globals(): 
        global _oprwarnobj
        _oprwarnobj=_Warnings()
    else:    
        _oprwarnobj=_Warnings()    
    
def warning(string):

    if '_oprwarnobj' not in globals(): warningClear() #if wipe is not called and _oprwarnobj(Object) is not created
    
    return _oprwarnobj(string)
