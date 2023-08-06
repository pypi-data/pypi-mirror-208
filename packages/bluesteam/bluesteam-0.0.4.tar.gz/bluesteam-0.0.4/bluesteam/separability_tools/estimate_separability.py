# -*- coding: utf-8 -*-
# Bluesteam
# Copyright (C) 2022-, Sarang Bhagwat <sarangb2@illinois.edu>
# 
# This module is under the MIT open-source license. See 
# github.com/BluestemBiosciences/bluesteam/LICENSE.txt
# for license details.
"""
"""
from bluesteam.separability_tools.utils import BlueStream, run_sequential_distillation, get_sorted_results
from thermosteam import Chemical
from datetime import datetime

#%% Run comparison
run_comparison = False
if run_comparison:
    # Inputs - these are a list of possible broth streams output from fermentation
    streams = [
        BlueStream(
            ID='AdAcG', # can customize this name; an auto-generated name will be given by default
            composition_dict = { # Keys: Chemicals; Use CAS IDs where unsure of names # Values: molar flows (kmol/h)
            'Water' : 1000,
            'AdipicAcid' : 20,
            'AceticAcid' : 20,
            'Glycerol' : 20,
            },
            products = ['AdipicAcid', 'AceticAcid', 'Glycerol'], # Chemicals; Use CAS IDs where unsure of names
            impurities = ['Water'] # Chemicals; Use CAS IDs where unsure of names
            ),
        
        BlueStream(
            ID='EtAcG',
            composition_dict = {
            'Water' : 1000,
            'Ethanol' : 20,
            'AceticAcid' : 20,
            'Glycerol' : 20,
            },
            products = ['Ethanol', 'AceticAcid', 'Glycerol'],
            impurities = ['Water']
            ),
        
        BlueStream(
            ID='AdG',
            composition_dict = {
            'Water' : 1000,
            'AdipicAcid' : 20,
            'Glycerol' : 20,
            },
            products = ['AdipicAcid', 'Glycerol'],
            impurities = ['Water']
            ),
        
        BlueStream(
            ID='Ad',
            composition_dict = {
            'Water' : 1000,
            'AdipicAcid' : 20,
            },
            products = ['AdipicAcid',],
            impurities = ['Water']
            ),
        
        ]
    
    # Add a few organic acid streams
    
    HP = Chemical('HP', search_ID='3-Hydroxypropionic acid')
    HP.copy_models_from(Chemical('LacticAcid'), names = ['V', 'Hvap', 'Psat', 'mu', 'kappa'])
    HP.Tm = 15 + 273.15 # CAS says < 25 C
    HP.Tb = 179.75 + 273.15 # CAS
    HP.Hf = Chemical('LacticAcid').Hf
    HP.default() # this defaults certain missing properties -- such as surface tension -- to that of water. Use with caution.
    
    MA = Chemical('Muconic acid', search_ID='3588-17-8')
    FDA = Chemical(ID='FDA', search_ID = '3238-40-2')
    
    
    orgacids = ['Levulinic Acid',
    'Adipic Acid',
    'Glutamic Acid',
    'Acetic Acid',
    'Acrylic Acid',
    'Salicylic Acid',
    'Itaconic Acid',
    FDA,
    'Glycolic Acid',
    'Formic Acid',
    # MA,
    HP,
    'Terephthalic Acid',
    'Succinic Acid']
    
    for acid in orgacids:
        acid_ID = acid
        if not type(acid) == str:
            acid_ID = acid.ID
        streams.append(BlueStream(
            ID=None,
            composition_dict = {
            'Water' : 1000,
            acid : 20,
            },
            products = [acid_ID,],
            impurities = ['Water'],
            ))
        
    # Save file with the current time in the name (for a custom file name, edit the file_to_save string)
    dateTimeObj = datetime.now()
    minute = '0' + str(dateTimeObj.minute) if len(str(dateTimeObj.minute))==1 else str(dateTimeObj.minute)
    file_to_save='bluesteam_separability_results_%s.%s.%s-%s.%s'%(dateTimeObj.year, dateTimeObj.month, dateTimeObj.day, dateTimeObj.hour, minute)
    
    # Run
    results = get_sorted_results(streams, print_results=True, file_to_save=file_to_save)

