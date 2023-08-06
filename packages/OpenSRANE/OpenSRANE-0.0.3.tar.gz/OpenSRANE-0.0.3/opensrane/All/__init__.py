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



pathdir=_os.path.dirname(__file__) #Get the current file path
#print(pathdir)
pathdir=pathdir.split("\\")
#print(pathdir)
pathdir="\\".join(pathdir[0:len(pathdir)-1])
#print(pathdir)


lstm=[x for x in _os.listdir(pathdir) if _os.path.isdir('\\'.join([pathdir,x]))==True and not x.startswith("_") and not x=="All"] #Get list of directories in the current file



TotalClassList=[] #name of all classes are also stored in this list

for folder in lstm: #for each folder
    a=[pathdir,folder] 
    npath='\\'.join(a) #Join the path and directory to get access to each folder 
    lst=_os.listdir(npath) #Get the list of the files exist in the folder
    lst=[x[:len(x)-3] for x in lst if x.endswith('.py') and not x.startswith('_') and not x.startswith('ObjManager')] #Get list of each py file
    
    classstr=f'{folder}_Classlist=[]' #For each folder we generate a list of classes for distiguishing the type of Objects
    exec(classstr)
    
    for i in lst: #Import all classes and functions in the folder
        importstr=f'from ..{folder}.{i} import *' #import string command
        exec(importstr)                 #Execute the string command line
        
        classstr=f'{folder}_Classlist.append(i)' #Appending each file name (beacuse each file should be a class) to the folder name
        exec(classstr)
        TotalClassList.append(i) #Also Appending all classes in Total Class list to have all of them

        

#del all above variables that aren't needed for future
del(importstr)
del(classstr)
del(a)
del(pathdir)
del(lstm)
del(npath)
del(lst)
del(folder)
del(i)