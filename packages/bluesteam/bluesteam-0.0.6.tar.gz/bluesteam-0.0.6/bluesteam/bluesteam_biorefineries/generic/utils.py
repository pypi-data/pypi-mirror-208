# -*- coding: utf-8 -*-
# Bluesteam
# Copyright (C) 2022-, Sarang Bhagwat <sarangb2@illinois.edu>
# 
# This module is under the MIT open-source license. See 
# github.com/BluestemBiosciences/bluesteam/LICENSE.txt
# for license details.
"""
"""
import numpy as np
import thermosteam as tmo
from thermosteam import Chemical, Stream
from bluesteam.bluesteam_biorefineries import generic

from bluesteam.bluesteam_biorefineries.generic._chemicals import create_chemicals
set_thermo = tmo.settings.set_thermo

__all__ = ('BlueStream', 'has_required_properties')


class BlueStream:
    def __init__(self,composition_dict,
                 products,
                 impurities,
                 fermentation_feed_glucose_flow,
                 ID=None):
        
        generic.load()
        corn_chems = create_chemicals()
        chems = [c for c in corn_chems]
        if not ID:
            ID = f's_{int(1e6*round(np.random.rand(), 6))}'
        
        for k in composition_dict.keys():
            if type(k)==str:
                try:
                    chem_k = corn_chems[k]
                    if not chem_k.sigma.method:
                        chem_k.copy_models_from(tmo.Chemical('Water'), ['sigma'])
                    chems.append(chem_k)
                except:
                    chem_k = Chemical(k)
                    if not chem_k.sigma.method:
                        chem_k.copy_models_from(tmo.Chemical('Water'), ['sigma'])
                    chems.append(chem_k)
            else:
                chem_k = k
                if not chem_k.sigma.method:
                    chem_k.copy_models_from(tmo.Chemical('Water'), ['sigma'])
                chems.append(chem_k)
        set_thermo(chems)
        
        self.ID = ID
        self.stream = stream = Stream(ID=ID)
        for k, v in composition_dict.items():
            if type(k)==str:
                stream.imol[k] = v
            else:
                stream.imol[k.ID] = v
        
        self.products = products
        self.impurities = impurities
        self.fermentation_feed_glucose_flow = fermentation_feed_glucose_flow
        
    def __repr__(self):
        self.stream.show('cmol100')
        return f''
  

def has_required_properties(chemical, required_properties=['Tb', 'Vl', 'Vg', 'Psat', 'Pc']):
    if type(chemical) == str:
        chemical = Chemical(chemical)
    missing_properties = chemical.get_missing_properties()
    for p in missing_properties:
        if p in required_properties:
            return False
    if 'V' in missing_properties:
        if 'Vs' in required_properties and not chemical.V.s.method:
            return False
        elif 'Vl' in required_properties and not chemical.V.l.method:
            return False
        elif 'Vg' in required_properties and not chemical.V.g.method:
            return False
    if 'Pc' in required_properties and not chemical.Pc:
        return False
    return True
