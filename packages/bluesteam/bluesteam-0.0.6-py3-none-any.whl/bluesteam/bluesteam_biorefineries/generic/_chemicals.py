# -*- coding: utf-8 -*-
# Bluesteam
# Copyright (C) 2022-, Sarang Bhagwat <sarangb2@illinois.edu>,
# 		       Yoel Cortes-Pena <yoelcortes@gmail.com>
# 
# This module is under the MIT open-source license. See 
# github.com/BluestemBiosciences/bluesteam/LICENSE.txt
# for license details.
"""
"""
from thermosteam import functional as fn
import thermosteam as tmo

__all__ = ('create_chemicals',)
_cal2joule = 4.184

def create_chemicals():
    from biorefineries import lipidcane as lc
    # from biorefineries import cornstover as cs
    chemicals = lc.chemicals['Water', 'Ethanol', 'Glucose', 'H3PO4', 'P4O10', 
                             # 'CO2', 'Octane', 'O2', 'CH4', 'Ash', 
                             'CO2', 'Octane', 'CH4', 'Ash', 
                             'Yeast', 'CaO', 'TAG', 'Cellulose']
    # chemicals += cs.chemicals['H2SO4', 'N2', 'SO2']
    # chemicals += cs.chemicals['H2SO4', 'SO2']
    chemicals += [tmo.Chemical('H2SO4'), tmo.Chemical('SO2')]
    chemicals += [tmo.Chemical('O2'), tmo.Chemical('N2', tmo.Chemical('Sucrose'))]
    CSL = tmo.Chemical.blank('CSL', phase='l', formula='CH2.8925O1.3275N0.0725S0.00175', 
                          Hf=-17618*_cal2joule/4+lc.chemicals['Water'].Hf/2+(-682502.448)/4)
    DAP = tmo.Chemical('DAP', search_ID='DiammoniumPhosphate',
                          phase='l', Hf= -283996*_cal2joule)
    CSL.phase_ref = 'l'
    DAP.phase_ref = 'l'
    CSL.at_state('l')
    DAP.at_state('l')
    def set_rho(chemical, rho):       
        V = fn.rho_to_V(rho, chemical.MW)
        chemical.V.add_model(V, top_priority=True)
    set_rho(CSL, 1e5)
    set_rho(DAP, 1e5)
    CSL.default()
    DAP.default()
    
    chemicals += [CSL, DAP]
    chemicals = tmo.Chemicals([*chemicals, 'NH3'])
    Starch = chemicals.Cellulose.copy('Starch', aliases=())
    Fiber = chemicals.Cellulose.copy('Fiber', aliases=())
    SolubleProtein = chemicals.Cellulose.copy('SolubleProtein', aliases=())
    InsolubleProtein = chemicals.Cellulose.copy('InsolubleProtein', aliases=())
    chemicals.extend([Starch, Fiber, SolubleProtein, InsolubleProtein])
    chemicals.NH3.at_state('l')
    chemicals.compile()
    chemicals.set_synonym('TAG', 'Oil')
    chemicals.set_synonym('TAG', 'Lipid')
    chemicals.set_synonym('Water', 'H2O')
    return chemicals