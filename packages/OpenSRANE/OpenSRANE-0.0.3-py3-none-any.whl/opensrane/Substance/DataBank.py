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


from .Material import Material as _Material

class DataBank():
    
    '''
    Units in SI:
    mass: kg
    length: m
    moloclue number: mol
    Energy: J
    Temperature: Kelvin
    
    force: N
    pressure: N/m2                                    #(1bar=10^5 N/m2)
    Energy: w(watt)=J/s= kg.m^2/s^3                   #https://en.wikipedia.org/wiki/Watt#:~:text=The%20watt%20(symbol%3A%20W),m2%E2%8B%85s%E2%88%923.    
    
    ATTENTION: LFL and UFL should enter as density unit (kg/m3)
    
    '''
    
   
    @staticmethod
    def Dimethylhydrazine(tag):
        obj=_Material(tag)
        obj.name="Dimethylhydrazine"
        obj.Vapour_Density=2.0746                       #SI unit: kg/m3
        obj.Stoichiometric_Concentration=2              #SI unit: %       https://rapidn.jrc.ec.europa.eu/substance/1-1-dimethylhydrazine
        obj.Molecular_Weight=60.1/1000                  #SI unit: kg/mol  https://rapidn.jrc.ec.europa.eu/substance/1-1-dimethylhydrazine
        obj.Molar_Volume=76.764*100**(-3)               #SI unit: m3/mol  https://rapidn.jrc.ec.europa.eu/substance/1-1-dimethylhydrazine
        obj.Density=790                                 #SI unit: kg/m3
        obj.Boiling_Point=63.9+273                      #SI unit: Kelvin  https://rapidn.jrc.ec.europa.eu/substance/1-1-dimethylhydrazine
        obj.Vapour_Pressure=20932                       #Si unit: N/m2    https://rapidn.jrc.ec.europa.eu/substance/1-1-dimethylhydrazine
        obj.Specific_Heat_of_Vaporization=607000        #SI unit: J/kg    ((latent) heat of vaporization or heat of evaporation or  enthalpy of vaporization (symbol ∆Hvap)
        obj.Vapour_Pressure=13732.2 #Pa at 25 Deg C
        obj.Liquid_Partial_Pressure_in_Atmosphere=0     #!!!!!!!!!!Not Sure!!!!!! 
        obj.Melting_Point=-58+273                       #SI unit: Kelvin
        obj.Flash_Point=-15+273
        obj.Lower_Flammability_Limit=0.0415            #Valid [x] > 0 kg/m3 (0.02*2.0746)
        obj.Upper_Flammability_Limit=1.971             #Valid [x] > 0 kg/m3 (0.95*2.0746)    
        
  
        
        return obj
        
    @staticmethod
    def Butene(tag):
        obj=_Material(tag)
        obj.name="Butene"
        obj.Molar_Heat_of_Combustion=2541.3*1000                #SI unit: J/mol   https://rapidn.jrc.ec.europa.eu/substance/108?__data=9623
        obj.Vapour_Density=2.4496                               #SI unit: kg/m3   https://encyclopedia.airliquide.com/1-butene
        obj.GasDensity=2.602                                    #SI unit: kg/m3   https://encyclopedia.airliquide.com/1-butene#properties
        obj.Stoichiometric_Concentration=3.374
        obj.Molecular_Weight=56.11/1000                         #SI unit: kg/mol  https://encyclopedia.airliquide.com/1-butene#properties
        obj.Molar_Volume=89.007*100**(-3)                       #m3/mol
        obj.Density=625                                         #SI unit: kg/m3  https://encyclopedia.airliquide.com/1-butene
        obj.Boiling_Point=273-6.3                               #SI unit: Kelvin http://www.chemspider.com/Chemical-Structure.7556.html?rid=6e9562d8-c239-4040-9628-b5a8e33c1edf&page_num=0
        obj.Specific_Heat_Ratio=1.1225                          # (@25 C)  or Cp/Cv ratio γ or Heat capacity ratio or ratio of specific heats, or Laplace's coefficient
        obj.Specific_Heat_of_Combustion=45.334*10**6            #SI unit: J/kg   http://www.thermalfluidscentral.org/encyclopedia/index.php/Heat_of_Combustion
        obj.Lower_Flammability_Limit=0.03903                    #kg/m3    (2.602*1.5/100) https://encyclopedia.airliquide.com/1-butene#safety-compatibility
        obj.Upper_Flammability_Limit=0.276                      #kg/m3    (2.602*10.6/100) https://encyclopedia.airliquide.com/1-butene#safety-compatibility
        obj.Specific_Heat_of_Vaporization=392.23*1000           #SI unit: J/kg  https://encyclopedia.airliquide.com/1-butene#properties
        obj.Liquid_Partial_Pressure_in_Atmosphere=2.57*10**3    #Si unit: N/m2 of Pa
        obj.Vapour_Pressure=4932.93                             #Pa    http://www.chemspider.com/Chemical-Structure.7556.html?rid=6e9562d8-c239-4040-9628-b5a8e33c1edf&page_num=0  
        obj.Melting_Point=-185+273                              #SI unit: Kelvin  http://www.chemspider.com/Chemical-Structure.7556.html?rid=6e9562d8-c239-4040-9628-b5a8e33c1edf&page_num=0
        
        return obj

    
    @staticmethod
    def propane(tag):
        obj=_Material(tag)
        obj.name="propane"
        obj.Specific_Heat_Ratio=1.136                     #@25 C https://encyclopedia.airliquide.com/propane#properties
        obj.Molecular_Weight=44.1/1000
        obj.GasDensity=1.898                              #at 25 °C (77 °F) https://encyclopedia.airliquide.com/propane#properties
        obj.Density=564                                   # http://www.chemspider.com/Chemical-Structure.6094.html?rid=0cc835e9-7e13-4568-b050-de0484a1f89f
        obj.Specific_Heat_of_Vaporization=428000          #J/kg https://www.engineeringtoolbox.com/fluids-evaporation-latent-heat-d_147.html
        obj.Liquid_Partial_Pressure_in_Atmosphere=1823.85
        obj.Vapour_Pressure=935618.56 #Pa at 25 Deg C
        obj.Boiling_Point=273-42                          #SI unit: Kelvin  http://www.chemspider.com/Chemical-Structure.6094.html?rid=0cc835e9-7e13-4568-b050-de0484a1f89f 
        obj.Melting_Point=-188+273                        #SI unit: Kelvin  http://www.chemspider.com/Chemical-Structure.6094.html?rid=0cc835e9-7e13-4568-b050-de0484a1f89f
        
        return obj    
        
        
    @staticmethod
    def Octane(tag):
        obj=_Material(tag)
        obj.name="Octane (nOctane)"
        obj.Vapour_Density=3.94                            #https://rapidn.jrc.ec.europa.eu/substance/257?__data=1229
        obj.Stoichiometric_Concentration=1.9/100           # % https://rapidn.jrc.ec.europa.eu/substance/257?__data=1229
        obj.Molecular_Weight=114.232/1000                  #kg/mol   https://rapidn.jrc.ec.europa.eu/substance/257?__data=1229
        obj.Molar_Volume=None
        obj.Density=0.703*1000                             #https://en.wikipedia.org/wiki/Octane
        obj.Boiling_Point=125.6+273                        #Kelvin https://rapidn.jrc.ec.europa.eu/substance/257?__data=1229
        obj.Vapour_Pressure=1.47*10**3                     #Pa at 20 Deg C   https://en.wikipedia.org/wiki/Octane
        obj.Specific_Heat_of_Vaporization=298000           #[J/kg]   https://www.engineeringtoolbox.com/fluids-evaporation-latent-heat-d_147.html
        obj.Vapour_Pressure=1.47*10**3                     #Pa at 25 Deg C  https://en.wikipedia.org/wiki/Octane
        obj.Liquid_Partial_Pressure_in_Atmosphere=0        #!!!!!!!NotSure!!!!! 
        obj.Melting_Point=-56.89+273                        #SI unit: Kelvin https://rapidn.jrc.ec.europa.eu/substance/257?__data=1229
        obj.Lower_Flammability_Limit=0.95/100               #https://rapidn.jrc.ec.europa.eu/substance/257?__data=1229

        return obj
        
    @staticmethod
    def n_hexane(tag): 
        obj=_Material(tag)
        obj.name="n_hexane"
        obj.GasDensity=3.23                                # kg/m3  https://encyclopedia.airliquide.com/hexane#properties 
        obj.Molecular_Weight=86.175/1000                   # kg/mol https://encyclopedia.airliquide.com/hexane#properties
        obj.Specific_Heat_of_Vaporization=334.933*1000     # [J/kg] https://encyclopedia.airliquide.com/hexane#properties
        obj.Boiling_Point=68.71+273                        # Kelvin https://encyclopedia.airliquide.com/hexane#properties
        obj.Density=232.28                                 # kg/m3  https://encyclopedia.airliquide.com/hexane#properties
        obj.Melting_Point=-95.32+273                       # Kelvin https://encyclopedia.airliquide.com/hexane#properties
        obj.Lower_Flammability_Limit=0.0323                # kg/m3 https://encyclopedia.airliquide.com/hexane#safety-compatibility (0.01*3.23)
        obj.Upper_Flammability_Limit=0.288                 # kg/m3 https://encyclopedia.airliquide.com/hexane#safety-compatibility (8.9/100*3.23)
        obj.Flash_Point=-20+273                            # https://encyclopedia.airliquide.com/hexane#safety-compatibility
        obj.Autoignition_Temperature=230+273               # https://encyclopedia.airliquide.com/hexane#safety-compatibility
        obj.Molar_Volume=0.37*10**(-3)                     # m3/mol 
        obj.Liquid_Partial_Pressure_in_Atmosphere=0        # CascalBook example 2.9
        return obj
        
        
    @staticmethod
    def CasCalEx2_1(tag):
        obj=_Material(tag)
        obj.name="CasCalEx2_1"
        obj.Density=867.0
        


        return obj

        
    @staticmethod
    def Gasoline(tag):
        obj=_Material(tag)
        obj.name="Gasoline"
        obj.Density=750                                          #SI unit: kg/m3   https://rapidn.jrc.ec.europa.eu/substance/gasoline?__data=8713
        obj.Molar_Heat_of_Combustion=4612.5*1000                 #SI unit: J/mol   https://rapidn.jrc.ec.europa.eu/substance/gasoline?__data=8713
        obj.Vapour_Density=3.5381                                #SI unit: kg/m3   https://rapidn.jrc.ec.europa.eu/substance/gasoline?__data=8713
        obj.Molecular_Weight=102.5*10**(-3)                      #SI unit: kg/mol  https://rapidn.jrc.ec.europa.eu/substance/gasoline?__data=8713
        obj.Molar_Volume=138.51*100**(-3)                        #SI unit: m3/mol  https://rapidn.jrc.ec.europa.eu/substance/gasoline?__data=8713
        obj.Boiling_Point=273+55                                 #SI unit: Kelvin  https://rapidn.jrc.ec.europa.eu/substance/gasoline?__data=8713 (26.67~225) 
        obj.Melting_Point=-56.8+273                              #SI unit: Kelvin  https://rapidn.jrc.ec.europa.eu/substance/gasoline?__data=8713
        obj.Vapour_Pressure=53329                                #SI unit: Pa      https://rapidn.jrc.ec.europa.eu/substance/gasoline?__data=8713
        obj.Specific_Heat_of_Vaporization=348.9*1000             #SI unit: J/kg    https://rapidn.jrc.ec.europa.eu/substance/gasoline?__data=8713
        obj.Specific_Heat_Capacity=2220                          #SI unit: J/kg.k  https://rapidn.jrc.ec.europa.eu/substance/gasoline?__data=8713
        obj.Molar_Heat_Capacity=227.5                            #SI unit: J/mol.k https://rapidn.jrc.ec.europa.eu/substance/gasoline?__data=8713
        obj.Specific_Heat_of_Combustion=45*10**6                 #SI unit: J/kg    https://rapidn.jrc.ec.europa.eu/substance/gasoline?__data=8713
        obj.Autoignition_Temperature=273+280                     #SI unit: Kelvin  https://rapidn.jrc.ec.europa.eu/substance/gasoline?__data=8713
        obj.Flash_Point=-43+273                                  #SI unit: Kelvin  https://rapidn.jrc.ec.europa.eu/substance/gasoline?__data=8713
        obj.Lower_Flammability_Limit=0.0496                      #SI unit: kg/m3   https://rapidn.jrc.ec.europa.eu/substance/gasoline?__data=8713 (1.4/100x3.5381)=0.0496 
        obj.Upper_Flammability_Limit=0.27                        #SI unit: kg/m3   https://rapidn.jrc.ec.europa.eu/substance/gasoline?__data=8713 (7.6/100x3.5381)=0.27  
        obj.Specific_Heat_Ratio=1.535                            #[http://dx.doi.org/10.1088/1755-1315/770/1/012065]  Cp/Cv ratio γ or Heat capacity ratio or ratio of specific heats, or Laplace's coefficient
        obj.Liquid_Partial_Pressure_in_Atmosphere=8.477*10**3    #Si unit: N/m2 of Pa
        return obj