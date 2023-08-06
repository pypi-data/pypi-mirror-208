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


#Rules: Each file present a class  that the name of the class should be exactly equal to file name

import os as _os
def Pyfileslist():
    '''
    This function returns list of the python files in the current directory
    '''
    pathdir=_os.path.dirname(__file__) #Get the current running file path
    lst=_os.listdir(pathdir) #Get the list of the files exist in the current __init__ file directory
    lst=[x[:len(x)-3] for x in lst if x.endswith('.py') and not x.startswith('_')]
    return lst

lst=Pyfileslist() #list of *.py files that is list of classes

for i in lst: #Import all classes
    importstr=f'from .{i} import *' #import string command
    exec(importstr)                 #Execute the string command line

del(lst)
del(i)
del(Pyfileslist)
del(importstr)