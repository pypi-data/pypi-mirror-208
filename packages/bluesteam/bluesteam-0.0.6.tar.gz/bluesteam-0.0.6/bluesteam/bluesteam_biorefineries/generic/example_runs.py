# -*- coding: utf-8 -*-
# Bluesteam
# Copyright (C) 2022-, Sarang Bhagwat <sarangb2@illinois.edu>
# 
# This module is under the MIT open-source license. See 
# github.com/BluestemBiosciences/bluesteam/LICENSE.txt
# for license details.
"""
"""
from bluesteam.bluesteam_biorefineries import generic
from bluesteam.bluesteam_biorefineries.generic._bluestea import BluesTEA
from bluesteam.bluesteam_biorefineries.generic.utils import BlueStream, has_required_properties
import thermosteam as tmo

#%% Disable numba 
# import os
# os.environ['NUMBA_DISABLE_JIT'] = '1'

#%% Example_1
MPO = tmo.Chemical(ID='MPO', search_ID='2-methyl-1-propanol')
stream_1 = BlueStream(
        ID='stream_1',
        composition_dict = {
        "Water": 6618.481179294014,
        "AdipicAcid": 154.89413990078867,
        "Yeast": 20,
        "LacticAcid": 17.884760112870275,
        "AceticAcid": 10.791860228730412,
        MPO: 86.31073179134295,
        "CO2": 250.04038489513735
        },
        products = ['AdipicAcid',],
        impurities = ['Water', 
                      'LacticAcid',
                      'AceticAcid',
                       "MPO",
                       
                      ],
        fermentation_feed_glucose_flow = 265 ,
        )

tea_1 = BluesTEA(
    system_ID = 'sys1',
                # system_ID=stream_1.ID+'_sys',
                  bluestream=stream_1,
                  upstream_feed='corn',
                  upstream_feed_capacity=stream_1.fermentation_feed_glucose_flow,
                  upstream_feed_capacity_units='kmol-Glucose-eq/h',
                 products_and_purities={'AdipicAcid':0.99}, # {'product ID': purity in weight%}
                 products_and_market_prices={'AdipicAcid':1.75}, # {'product ID': price in $/pure-kg})
                 current_equipment=None,
                 fermentation_residence_time=100., # h
                 aeration_rate=15e-3,
                 )

#%% Simulated differential solubilities of organic acids in the flashed broth for Example_1

s1 = tea_1.flowsheet.unit.S401_1_crystallizer.ins[0].copy()
print('\nStream entering the crystallizer:')
s1.show('cwt100')

print('\nStream after chilling to 3.67 degC and performing solid-liquid equilibrium:')
s1.T= 3.67 + 273.15
for solute in ['AdipicAcid', 'AceticAcid', 'LacticAcid', 'MPO']:
    s1.sle(T=s1.T, P=s1.P, solute=solute)
s1.show('cwt100')

print('\nStream with 50 wt% Acetic acid after chilling to 3.67 degC and performing solid-liquid equilibrium:')
s2 = tmo.Stream('s2')
s2.imass['Water']=1000
s2.imass['AceticAcid'] = 1000
s2.T = 3.67 + 273.15
s2.sle(T=s2.T, P=s2.P, solute='AceticAcid')
s2.show('cwt100')

print('\nStream with 50 wt% Lactic acid after chilling to 3.67 degC and performing solid-liquid equilibrium:')
s2 = tmo.Stream('s2')
s2.imass['Water']=1000
s2.imass['LacticAcid'] = 1000
s2.T = 3.67 + 273.15
s2.sle(T=s2.T, P=s2.P, solute='LacticAcid')
s2.show('cwt100')

print('\nStream with 50 wt% Adipic acid after chilling to 3.67 degC and performing solid-liquid equilibrium:')
s2 = tmo.Stream('s2')
s2.imass['Water']=1000
s2.imass['AdipicAcid'] = 1000
s2.T = 3.67 + 273.15
s2.sle(T=s2.T, P=s2.P, solute='AdipicAcid')
s2.show('cwt100')

#%% Example_2
LacticAcid = tmo.Chemical('LacticAcid')
HP = tmo.Chemical(ID='HP', search_ID='3-hydroxypropionic acid')
HP.copy_models_from(LacticAcid, names = ['V', 'Hvap', 'Psat', 'mu', 'kappa'])
HP.Tm = 15 + 273.15 # CAS says < 25 C
HP.Tb = 179.75 + 273.15 # CAS
HP.Hf = LacticAcid.Hf
HP.Pc = LacticAcid.Pc
Ethanol = tmo.Chemical(ID="id_ethanol",search_ID='ethanol')

stream_2 = BlueStream(
        ID='stream_2',
        composition_dict = {
        "water": 6331.54716019406,
       HP: 496.4281386457651,
       "Yeast": 20,
       "LacticAcid": 17.884760112870275,
       "AceticAcid": 10.791860228730412,
       Ethanol: 3.556724191556348,
       "SuccinicAcid": 7.113448383112774
        },
        products = ['HP',],
        impurities = [
            "water",
            "LacticAcid",
            "AceticAcid",
            "id_ethanol",
            "SuccinicAcid",
                       
                      ],
        fermentation_feed_glucose_flow = 265 ,  
        )

tea_2 = BluesTEA(
    system_ID = 'sys1',
                # system_ID=stream_2.ID+'_sys',
                  bluestream=stream_2,
                  upstream_feed='sucrose',
                  upstream_feed_capacity=stream_2.fermentation_feed_glucose_flow,
                  upstream_feed_capacity_units='kmol-Glucose-eq/h',
                 products_and_purities={'HP':0.99}, # {'product ID': purity in weight%}
                 products_and_market_prices={'HP':1.75}, # {'product ID': price in $/pure-kg})
                 current_equipment=None,
                 fermentation_residence_time=100., # h
                 aeration_rate=15e-3,
                 )

#%% Example_3
LacticAcid = tmo.Chemical('LacticAcid')
HP = tmo.Chemical(ID='HP', search_ID='3-hydroxypropionic acid')
HP.copy_models_from(LacticAcid, names = ['V', 'Hvap', 'Psat', 'mu', 'kappa'])
HP.Tm = 15 + 273.15 # CAS says < 25 C
HP.Tb = 179.75 + 273.15 # CAS
HP.Hf = LacticAcid.Hf
HP.Pc = LacticAcid.Pc

stream_3 = BlueStream(
        ID='stream_3',
        composition_dict = {
        "water": 6331.54716019406,
       HP: 508.28819656562774,
       "Yeast": 20,
       "LacticAcid": 17.884760112870275,
       "AceticAcid": 10.791860228730412,
        },
        products = ['HP',],
        impurities = [
            "water",
            "LacticAcid",
            "AceticAcid",
                       
                      ],
        fermentation_feed_glucose_flow = 265 ,  
        )

tea_3 = BluesTEA(
    system_ID = 'sys1',
                # system_ID=stream_3.ID+'_sys',
                  bluestream=stream_3,
                  upstream_feed='sucrose',
                  upstream_feed_capacity=stream_3.fermentation_feed_glucose_flow,
                  upstream_feed_capacity_units='kmol-Glucose-eq/h',
                 products_and_purities={'HP':0.99}, # {'product ID': purity in weight%}
                 products_and_market_prices={'HP':1.75}, # {'product ID': price in $/pure-kg})
                 current_equipment=None,
                 fermentation_residence_time=100., # h
                 aeration_rate=15e-3,
                 )

#%% Example_4
APO = tmo.Chemical(ID='APO', search_ID='azepan-2-one')

stream_4 = BlueStream(
        ID='stream_4',
        composition_dict = {
        "water": 6807.791760751999,
        APO: 203.31527862625188,
        "Yeast": 20,
        "LacticAcid": 17.884760112870275,
        "AceticAcid": 10.791860228730412,
        "CO2": 304.86207356198526
        },
        products = ['APO',],
        impurities = [
            "water",
            "LacticAcid",
            "AceticAcid",
                       
                      ],
        fermentation_feed_glucose_flow = 265 ,  
        )

tea_4 = BluesTEA(
    system_ID = 'sys1',
                # system_ID=stream_4.ID+'_sys',
                  bluestream=stream_4,
                  upstream_feed='sucrose',
                  upstream_feed_capacity=stream_4.fermentation_feed_glucose_flow,
                  upstream_feed_capacity_units='kmol-Glucose-eq/h',
                 products_and_purities={'APO':0.99}, # {'product ID': purity in weight%}
                 products_and_market_prices={'APO':1.75}, # {'product ID': price in $/pure-kg})
                 current_equipment=None,
                 fermentation_residence_time=100., # h
                 aeration_rate=15e-3,
                 )

#%% Example_5
Butanol = tmo.Chemical(ID='Butanol', search_ID='n-butanol')

stream_5 = BlueStream(
        ID='stream_5',
        composition_dict = {
        "water": 6554.027140435833,
        Butanol: 254.14409828281325,
        "Yeast": 20,
        "LacticAcid": 17.884760112870275,
        "AceticAcid": 10.791860228730412,
        "CO2": 508.10345593664937
        },
        products = ['Butanol',],
        impurities = [
            "water",
            "LacticAcid",
            "AceticAcid",
                       
                      ],
        fermentation_feed_glucose_flow = 265 ,  
        )

tea_5 = BluesTEA(
    system_ID = 'sys1',
                # system_ID=stream_5.ID+'_sys',
                  bluestream=stream_5,
                  upstream_feed='sucrose',
                  upstream_feed_capacity=stream_5.fermentation_feed_glucose_flow,
                  upstream_feed_capacity_units='kmol-Glucose-eq/h',
                 products_and_purities={'Butanol':0.99}, # {'product ID': purity in weight%}
                 products_and_market_prices={'Butanol':1.75}, # {'product ID': price in $/pure-kg})
                 current_equipment=None,
                 fermentation_residence_time=100., # h
                 aeration_rate=15e-3,
                 )

#%% Example_6
BDO = tmo.Chemical(ID='BDO', search_ID='2,3-Butanediol')
BDO.Hf = -544.8	* 1000 # https://webbook.nist.gov/cgi/cbook.cgi?ID=C513859&Mask=FFF

stream_6 = BlueStream(
        ID='stream_6',
        composition_dict = {
        "water": 6437.895913598838,
        BDO: 277.2481072176166,
        "Yeast": 20,
        "LacticAcid": 17.884760112870275,
        "AceticAcid": 10.791860228730412,
        "CO2": 415.72100940270406
        },
        products = ['BDO',],
        impurities = [
            "water",
            "LacticAcid",
            "AceticAcid",
                       
                      ],
        fermentation_feed_glucose_flow = 265 ,  
        )

tea_6 = BluesTEA(
    system_ID = 'sys1',
                # system_ID=stream_6.ID+'_sys',
                  bluestream=stream_6,
                  upstream_feed='sucrose',
                  upstream_feed_capacity=stream_6.fermentation_feed_glucose_flow,
                  upstream_feed_capacity_units='kmol-Glucose-eq/h',
                 products_and_purities={'BDO':0.99}, # {'product ID': purity in weight%}
                 products_and_market_prices={'BDO':1.75}, # {'product ID': price in $/pure-kg})
                 current_equipment=None,
                 fermentation_residence_time=100., # h
                 aeration_rate=15e-3,
                 )

#%% Example_7 - this was just Example_6 without organic impurities

#%% Example_8
BDO = tmo.Chemical(ID='BDO', search_ID='1,4-Butanediol')

stream_8 = BlueStream(
        ID='stream_8',
        composition_dict = {
       "water": 6468.800723734534,
       BDO: 245.24905484291597,
        "Yeast": 20,
        "LacticAcid": 17.884760112870275,
        "AceticAcid": 10.791860228730412,
        "IsoamylAcetate": 18.519033854532868,
        "CO2": 414.03746087047836
        },
        products = ['BDO',],
        impurities = [
            "water",
            'LacticAcid',
            'AceticAcid',
            'IsoamylAcetate',
                       
                      ],
        fermentation_feed_glucose_flow = 265 ,  
        )

tea_8 = BluesTEA(
    system_ID = 'sys1',
                # system_ID=stream_8.ID+'_sys',
                  bluestream=stream_8,
                  upstream_feed='sucrose',
                  upstream_feed_capacity=stream_8.fermentation_feed_glucose_flow,
                  upstream_feed_capacity_units='kmol-Glucose-eq/h',
                 products_and_purities={'BDO':0.99}, # {'product ID': purity in weight%}
                 products_and_market_prices={'BDO':1.75}, # {'product ID': price in $/pure-kg})
                 current_equipment=None,
                 fermentation_residence_time=100., # h
                 aeration_rate=15e-3,
                 )

#%% Example_8
# BDO = tmo.Chemical(ID='BDO', search_ID='1,4-Butanediol')
# Ethanol = tmo.Chemical(ID="EtOH",search_ID='ethanol')

stream_8 = BlueStream(
        ID='stream_8',
        composition_dict = {
       # BDO: 245.24905484291597,
        'Ethanol': 250.,
        'Water': 1000.,
        },
        products = ['Ethanol',],
        impurities = [
            "water", "water",
                       
                      ],
        fermentation_feed_glucose_flow = 265 ,  
        )

tea_8 = BluesTEA(
    system_ID = 'sys1',
                # system_ID=stream_8.ID+'_sys',
                  bluestream=stream_8,
                  upstream_feed='sucrose',
                  upstream_feed_capacity=stream_8.fermentation_feed_glucose_flow,
                  upstream_feed_capacity_units='kmol-Glucose-eq/h',
                 products_and_purities={'Ethanol':0.99}, # {'product ID': purity in weight%}
                 products_and_market_prices={'Ethanol':1.75}, # {'product ID': price in $/pure-kg})
                 current_equipment=None,
                 fermentation_residence_time=100., # h
                 aeration_rate=15e-3,
                 )

