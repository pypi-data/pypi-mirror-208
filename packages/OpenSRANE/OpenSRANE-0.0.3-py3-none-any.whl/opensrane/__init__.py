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


import os as _os


pathdir=_os.path.dirname(__file__) #Get the current file path


lstm=[x for x in _os.listdir(pathdir) if _os.path.isdir('\\'.join([pathdir,x]))==True and not x.startswith("_")] #Get list of directories in the current file

#import All subpackages
for folder in lstm: #for each folder
    importstr=f'from opensrane import {folder}' #import string command
    exec(importstr)                 #Execute the string command line

#import Misc Commands
lstm=['Misc']
for folder in lstm: #for each folder
    a=[pathdir,folder] 
    npath='\\'.join(a) #Join the path and directory to get access to each folder 
    lst=_os.listdir(npath) #Get the list of the files exist in the folder
    lst=[x[:len(x)-3] for x in lst if x.endswith('.py') and not x.startswith('_') and not x.startswith('ObjManager')] #Get list of each py file
    
    for i in lst: #Import all classes and functions in the folder
        importstr=f'from .{folder}.{i} import *' #import string command
        exec(importstr)                 #Execute the string command line
        
        

# del all above variables that aren't needed for future
del(importstr)
del(a)
del(pathdir)
del(lstm)
del(npath)
del(lst)
del(folder)
del(i)
