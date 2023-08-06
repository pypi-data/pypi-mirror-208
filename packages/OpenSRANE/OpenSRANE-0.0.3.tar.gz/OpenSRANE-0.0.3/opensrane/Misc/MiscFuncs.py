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
import opensrane.Misc.WarningRecorder as _Rcm
import gc as _gc

class MiscFuncs():
    '''
    In this class Miscallenouse functions that are needed to work 
    with objects and classes are defined
    '''
    
    @staticmethod     #This decorator cause the function doesn't need any self and consequently it doesn't give me any usage error
    def GetPackagename():
        '''
        this function returns the current package name  (currently maybe seems a silly function
        Sample: 
                import opensrane as _opr
                print(_opr.GetPackagename())
        
        '''
        import os
        spldir=os.path.dirname(__file__).split('\\')
        return spldir[len(spldir)-2]
    
    @staticmethod     #This decorator cause the function doesn't need any self and consequently it doesn't give me any usage error
    def GetModules():
        '''
        this function gives the name of modules(subpackages) and their corresponding object
        sample:
                mod=_opr.GetModules()
                
                that each item has 2 values:
                
                mod[0][0] is the name of package or module  
                and
                mod[0][1] is its corresponding object
        
        '''

        
        import inspect #https://docs.python.org/3/library/inspect.html


        membs=inspect.getmembers(_opr) # get all members of an 
        modules=[]
        for name,obj in membs:
            if inspect.ismodule(obj) and not name=="opr" and not name=="_os":
                modules.append((name,obj))
       
        return modules 
    
    @staticmethod
    def GetClasses():
        '''
        this function gives the name of classes in all (subpackages) and their corresponding object and their parent subpackage name
        sample:
        
                cls=_opr.GetClasses()
                
                that each item has 3 values:
                
                cls[0][0] is the name of the class
                cls[0][1] is the corresponding object of the class
                cls[0][2] is the name of the parent module of class[0]
        '''

        
        import inspect #https://docs.python.org/3/library/inspect.html

        modules=GetModules() #Get all modules name and objects

        classes=[]    
        for module in modules:
            membs=inspect.getmembers(module[1])
            for name,obj in membs:
                if inspect.isclass(obj) and not name=='ObjManager' and not module[0]=='opr' :
                    
                    classes.append((name,obj,module[0]))
        
        return classes
        
    @staticmethod
    def GetClassParrentModule(Classname):
        '''
        This function returns the Parrent module (subpackage) name (and it's corresponding object that this consist a class with name Classname
        
        sample:
                import opensrane as _opr
                print(_opr.GetClassParrentModule('A'))
                
                if there were a class with name Classname in the a module or subpackage, so the program returns the
                name of module or subpackage and its corresponding object
        '''
        
        clss=_opr.GetClasses()
        modules=_opr.GetModules()
        
        try:
            mod=[x[2] for x in clss if x[0]==Classname][0]
            modobj=[x[1] for x in modules if x[0]==mod][0]
            rslt=[mod, modobj]
        except:
            print(f'There is no class with name {Classname}')
            rslt=None
        finally:
            return rslt
    
    @staticmethod
    def wipe():
        '''
        Clear memory from all objects
        '''
        
        modules=_opr.Misc.GetModules() #Get all modules
        for module in modules:   #for each modlue or package clear all objects
            module[1].ObjManager.clearall()
        
        #Remove Garbage variables
        _gc.collect() 
        #Reset Recorder Objects
        # _Rcm.warningClear()   (its true to add it here because when user click wipe it means that user wants to run new model and warning should restart from zero)
        
        #Clear ObjectRecorder Content (It's Not true to add it here because it may clear the recorded file!)
        # _Rcm.recordedObjectsClear()
    
    @staticmethod
    def wipeAnalysis():
        '''
        This function or method implement wipeAnalysis method for all objects
        and by this approach it clears all analysis results for objects and objects becomes ready for
        next analysis
        '''
        subpackages=_opr.Misc.GetModules() #Get all modules or subpackages
        for SubPackname,SubPackobj in subpackages:   #for each modlue or subpackage clear all objects
            for obj in SubPackobj.ObjManager.Objlst:
                obj.wipeAnalysis()
        
        
#We define All MiscFuncs Functions here to be also available in root opensrane
    
def GetPackagename():
    return _opr.Misc.MiscFuncs.GetPackagename()

def GetModules():
    return _opr.Misc.MiscFuncs.GetModules()

def GetClasses():
    return _opr.Misc.MiscFuncs.GetClasses()

def GetClassParrentModule(Classname):
    return _opr.Misc.MiscFuncs.GetClassParrentModule(Classname)
        
def wipe():
    return _opr.Misc.MiscFuncs.wipe()

def wipeAnalysis():
    return _opr.Misc.MiscFuncs.wipeAnalysis()