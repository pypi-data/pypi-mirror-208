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


class _NewClass():
    '''
    All new classes in each module or subpackage are child of this class
    
    '''

    #----- Fix Part for each class -----
    Title=None
    Taglst=[]
    objlst=[]
    TagObjDict={}
    #-----------------------------------
    
    
    def __init__(self,tag):
        
        #---- Fix Part for each class __init__ ----
        self.Classname=self.__class__.__name__
        self.tag=tag
        self.objlst.append(self)
        self.Taglst.append(tag)
        self.TagObjDict[tag]=self
        #------------------------------------------
        
        
        
    def wipeAnalysis(self):
        pass
        
    pass