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

class RectangNodes(_NewClass,_GlobalParameters):
    '''
    This class create nodes according a rectangle coordinates and number of meshes that define by user with constant intensity
    
    xRefPoint: x coordinate of the left bottom corner of the rectangle area
    yRefPoint: y coordinate of the left bottom corner of the rectangle area
    xDim: Dimension of the rectangle area in x direction
    yDim: Dimension of the rectangle area in y direction
    xMesh: An integer that shows the number of the meshs in x direction
    yMesh: An integer that shows the number of the meshs in y direction
    PointsHeight: An flout or double that determines the height of the nodes that vulnerability should be check (NOT A LIST, JUST A VALUE)
    Intensity: Intensity of the node (Intendity per Area). If node is Social it shows the crowd per area, if environmental shows the plants per area
    
    '''
    Title="RectangNodes"
    
    def __init__(self,tag, xRefPoint, yRefPoint, xDim, yDim, xMesh, yMesh, PointsHeight, Intensity,
                      pressure_probit_tag=None, radiation_probit_tag=None, Toxic_probit_tag=None, Type='Social'):
        
        
        #---- Fix Part for each class __init__ ----
        ObjManager.Add(tag,self)
        _NewClass.__init__(self,tag)
        #------------------------------------------
        
        _xMesh=int(xMesh)
        _yMesh=int(yMesh)
        
        _xMeshdim=xDim/_xMesh
        _yMeshdim=yDim/_yMesh
        
        _Area=_xMeshdim*_yMeshdim
        
        _x0=xRefPoint+_xMeshdim/2
        _y0=yRefPoint+_yMeshdim/2
        
        _xGlobalList=[]
        _yGlobalList=[]
        
        for x in range(_xMesh):
            for y in range(_yMesh):
                _xGlobalList.append(_x0+x*_xMeshdim)
                _yGlobalList.append(_y0+y*_yMeshdim)
                
        _zGlobalList=[PointsHeight for i in _yGlobalList]
        
        _GlobalParameters.__init__(self,Type=Type, xGlobalList=_xGlobalList, yGlobalList=_yGlobalList, zGlobalList=_zGlobalList, AreaList=[_Area]*len(_xGlobalList), IntensityList=[Intensity]*len(_xGlobalList),
                                        pressure_probit_tag=pressure_probit_tag, radiation_probit_tag=radiation_probit_tag, Toxic_probit_tag=Toxic_probit_tag)

        self.name=f"RectangNodes with tag={tag} "
        
        self.wipeAnalysis()
    
    def wipeAnalysis(self):
        # properties that are defined in _GlobalParameters should also be reset
        self.wipeAnalysisGlobal()
        
        # properties that are not constant and among each analysis will change should be define here        
        pass
