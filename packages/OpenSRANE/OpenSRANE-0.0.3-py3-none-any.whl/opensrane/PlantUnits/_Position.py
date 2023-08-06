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


class _Position():
    HGRPCoordinate=0  #Horizontal Global Reference Point Coordinate
    VGRPCoordinate=0  #Vertical Global Reference Point Coordinate
    
    def __init__(self,Horizontal_local_Coordinate,Vertical_local_Coordinate):
        
        self.Hlocal=Horizontal_local_Coordinate 
        self.Vlocal=Vertical_local_Coordinate
        self._Hglobal=_Position.HGRPCoordinate+Horizontal_local_Coordinate #Horizontal Global Coordinate
        self._Vglobal=_Position.VGRPCoordinate+Vertical_local_Coordinate   #Vertical Global Coordinate
        
    @property
    def HGlobal(self):
        self._Hglobal=_Position.HGRPCoordinate+self.Hlocal
        return self._Hglobal
        
    @HGlobal.setter
    def HGlobal(self,Value): #Global Horizontal Coordinate
        self._Hglobal=Value
        self.Hlocal=self._Hglobal-_Position.HGRPCoordinate
    
    @property
    def VGlobal(self): #Global Vertical Coordinate
        self._Vglobal=_Position.VGRPCoordinate+self.Vlocal
        return self._Vglobal
        
    @HGlobal.setter
    def VGlobal(self,Value):
        self._Vglobal=Value
        self.Vlocal=self._Vglobal-_Position.VGRPCoordinate    
    