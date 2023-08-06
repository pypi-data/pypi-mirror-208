# -*- coding: utf-8 -*-
# Bluesteam
# Copyright (C) 2022-, Sarang Bhagwat <sarangb2@illinois.edu>
# 
# This module is under the MIT open-source license. See 
# github.com/BluestemBiosciences/bluesteam/LICENSE.txt
# for license details.
"""
"""
from bluesteam.bluesteam_biorefineries import generic as corn
from biosteam import System
import thermosteam as tmo
from thermosteam import Stream


def load_set_and_get_upstream_sys(ID, bluestream=None, fermentation_tau=None, simulate=False, 
                                       aeration_rate=0.,
                                       aeration_time=None,
                                       upstream_feed='sucrose',
                                       upstream_feed_capacity=100., # kg/h
                                       thermo=None):
    if bluestream:
        tmo.settings.set_thermo(bluestream.stream.chemicals)
    corn.load()
    
    units = corn.flowsheet.unit
    streams = corn.flowsheet.stream
    V405 = units['V405']
    V307 = units['V307']
    V307.ins[5].disconnect_source()
    
    
    
    
    if not aeration_time:
        aeration_time = V405.tau
    V405.aeration_time = aeration_time
    V405.aeration_rate = aeration_rate    
    if bluestream:
        V405.load_broth(bluestream)
        V405.outs[0].disconnect_sink()
        V405.outs[1].sink.outs[0].disconnect_sink()
    if fermentation_tau:
        V405.load_tau(fermentation_tau)

    
    if upstream_feed=='corn':
        if upstream_feed_capacity:
            streams['corn'].F_mass = upstream_feed_capacity
        
    elif upstream_feed=='sucrose':
        sucrose = Stream('sucrose')
        if upstream_feed_capacity:
            sucrose.imass['Glucose'] = upstream_feed_capacity
        else: 
            sucrose.imass['Glucose'] = 100.
        V405.ins[0] = sucrose
    
    
    # if units_till_fermentation:
    #     for unit in units_till_fermentation:
            # unit.simulate()
    
    for unit in list(corn.flowsheet.unit):
        try:
            unit.simulate()
        except:
            pass
    
    bluestream.stream.F_mol *= V405.ins[0].imol['Glucose']/bluestream.fermentation_feed_glucose_flow # initial scaling for bluestream total flow
        
    units_till_fermentation = V405.get_upstream_units()
    V405.simulate()
    
    # V405.show()
    
    new_sys = System.from_units(ID=ID, units=list(units_till_fermentation)+[V405, V405.outs[1].sink])
    if simulate:
        new_sys.simulate()
    return new_sys