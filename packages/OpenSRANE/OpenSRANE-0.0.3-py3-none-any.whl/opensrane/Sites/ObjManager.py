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


class _Classitterator(type):
    #This class is for making iteration on class name
    
    def __iter__(self):
        for param in (self.Objlst):
            yield param

class ObjManager(metaclass=_Classitterator): #metaclass is used to inheritage _Classitterator to make ObjManager iteratable
    
    Taglst=[]
    Objlst=[]
    TagObjDict={}
    
    @staticmethod
    def Check(tag):
        '''
        A boolean function
        This function checks that does this tag Created before or not.
        '''
        if tag in ObjManager.Taglst:
            return False
        else:
            return True
    
    @staticmethod
    def Add(tag,obj):
        '''
        This function Add the tag of the new object and it's corresponding Object to the list of Tags and 
        Objects and the distionary
        If it encounter with a repitative tag, an Error will be aroused
        '''
        if tag in ObjManager.Taglst:
            raise Exception('OpenSRANE Err: This is a repitative tag and it should be changed')
        else:   
            ObjManager.Taglst.append(tag)
            ObjManager.Objlst.append(obj)
            ObjManager.TagObjDict[tag]=obj
    
    @staticmethod
    def clearall(): #to clear all objects from 
        
        '''
        This function clears All objects and Tags created from the classes in the module that its 
        ObjManager is located. 
        
        '''
        
        directory_path = _os.path.dirname(__file__) #Find the current Directory path
        modulename = _os.path.basename(directory_path) #Current dirtectory name that is the name of the module or subpackage
        moduleObj=[x[1] for x in _opr.GetModules() if x[0]==modulename][0] #Get the object of the module or subpackage
        
        classlist=set() #Find the class objects that objects are created from them
        for i in moduleObj.ObjManager.Objlst:   #ّFind the all class objects in the current module or subpackage
            classlist.add(i.__class__)   
            
        for i in classlist: #For each class empty the Taglst and Objlst
            i.Taglst=[]
            i.objlst=[]        
        
        ObjManager.Objlst=[] #Also here remove all objects that are stored in ObjManager
        ObjManager.Taglst=[]
        ObjManager.TagObjDict={}
        
    def __class_getitem__(cls,tag):
        
        if tag in cls.Taglst:
            return cls.TagObjDict[tag]
        else:
            return "This tag has not been defined Yet"         