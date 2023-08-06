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


from opensrane.Misc._NewClass import _NewClass
from .ObjManager import *
from opensrane.Misc.WarningRecorder import *
from ._GlobalParameters import _GlobalParameters
import math as _math

class Nodes(_NewClass,_GlobalParameters):
    '''
    This class create nodes according data that directly be specify by user
    
        Type: that defines content of the node: Social, Environmental , ...
        xGlobalList: Global xcoordinate of the nodes
        yGlobalList: Global ycoordinate of the nodes
        zGlobalList: Global zcoordinate of the nodes
        AreaList: Area of the defined nodes that considered as rectangular and along main axis
        IntensityList: Intensity of the node (Intendity per Area). If node is Social show the crowd per area, if environmental shows the plants per area
        
    '''
    Title="Nodes"
    
    def __init__(self,tag, xGlobalList, yGlobalList, zGlobalList, AreaList, IntensityList,
                     pressure_probit_tag=None, radiation_probit_tag=None, Toxic_probit_tag=None,Type='Social'):
        
        if type(xGlobalList)!=list or type(xGlobalList)!=list or type(xGlobalList)!=list or type(xGlobalList)!=list:
            warning(f'(Nodes) Nodes with tag={tag} has not been created because type of xGlobalList or yGlobalList or AreaList or IntensityList is not equal list')
            return None
        
        #---- Fix Part for each class __init__ ----
        ObjManager.Add(tag,self)
        _NewClass.__init__(self,tag)
        #------------------------------------------
        
       
        #Check Dimensions and modify them if needed
        lenmin=min(len(xGlobalList),len(yGlobalList),len(zGlobalList),len(AreaList),len(IntensityList))
        lenmax=max(len(xGlobalList),len(yGlobalList),len(zGlobalList),len(AreaList),len(IntensityList))
        
        if lenmin!=lenmax:
            warning(f'(Nodes) Nodes with tag {tag}, length of the lists are not equal and they considered as minimum length')
            xGlobalList=xGlobalList[0:lenmin]
            yGlobalList=yGlobalList[0:lenmin]
            zGlobalList=zGlobalList[0:lenmin]
            AreaList=AreaList[0:lenmin]
            IntensityList=IntensityList[0:lenmin]
        
        # Finilizing the Object and evluatig the values        
        _GlobalParameters.__init__(self,Type=Type, xGlobalList=xGlobalList, yGlobalList=yGlobalList, zGlobalList=zGlobalList, AreaList=AreaList,
                                        IntensityList=IntensityList, pressure_probit_tag=pressure_probit_tag, radiation_probit_tag=radiation_probit_tag,
                                        Toxic_probit_tag=Toxic_probit_tag)

        self.name=f"Nodes with tag={tag} "
        
        self.wipeAnalysis()
    
    def wipeAnalysis(self):
        # properties that are defined in _GlobalParameters should also be reset
        self.wipeAnalysisGlobal()
        
        # properties that are not constant and among each analysis will change should be define here        
        pass
        

        
        
        


        
