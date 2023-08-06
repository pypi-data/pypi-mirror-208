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
from biosteam.process_tools import UnitGroup
from bluesteam.bluesteam_biorefineries import generic as cn
from biorefineries.sugarcane import ConventionalEthanolTEA

__all__ = ('create_tea', 'tea_summary')

def create_tea(system,  IRR=0.15,
           duration=(2018, 2038),
           depreciation='MACRS7', income_tax=0.35,
           operating_days=330, lang_factor=4,
           construction_schedule=(0.4, 0.6), WC_over_FCI=0.05,
           labor_cost=2.3e6, fringe_benefits=0.4,
           property_tax=0.001, property_insurance=0.005,
           supplies=0.20, maintenance=0.01, administration=0.005,
           cls=ConventionalEthanolTEA,
               
               ):
    # return cls(system, IRR=0.15,
    #            duration=(2018, 2038),
    #            depreciation='MACRS7', income_tax=0.35,
    #            operating_days=330, lang_factor=4,
    #            construction_schedule=(0.4, 0.6), WC_over_FCI=0.05,
    #            labor_cost=2.3e6, fringe_benefits=0.4,
    #            property_tax=0.001, property_insurance=0.005,
    #            supplies=0.20, maintenance=0.01, administration=0.005)

    return cls(system=system,IRR=IRR,
                duration=duration,
                depreciation=depreciation, income_tax=income_tax,
                operating_days=operating_days, lang_factor=lang_factor,
                construction_schedule=construction_schedule, WC_over_FCI=WC_over_FCI,
                labor_cost=labor_cost, fringe_benefits=fringe_benefits,
                property_tax=property_tax, property_insurance=property_insurance,
                supplies=supplies, maintenance=maintenance, administration=administration)

def tea_summary():
    operating_days = cn.corn_tea.operating_days
    f = operating_days * 24
    ug = UnitGroup('biorefinery', cn.corn_tea.units)
    power_utilities = ug.power_utilities
    heat_utilities = ug.heat_utilities
    heating_utilities = [i for i in heat_utilities if i.duty * i.flow > 0]
    cooling_utilities = [i for i in heat_utilities if i.duty * i.flow < 0]
    FCI = cn.corn_tea.FCI
    FOC = cn.corn_tea.FOC
    maintenance = cn.corn_tea.maintenance * FCI
    
    dct = {
        'Material costs':
            {'Corn': f * cn.corn.cost ,
             'Denaturant': f * cn.denaturant.cost,
             'Enzymes': f * (cn.alpha_amylase.cost + cn.gluco_amylase.cost),
             'Yeast': f * cn.yeast.cost,
             'Other': f * sum([i.cost for i in (cn.ammonia, cn.sulfuric_acid, cn.lime)])},
         'Production':
             {'Ethanol [MMgal / yr]': f * cn.ethanol.F_mass / 2.987 / 1e6,
              'DDGS [MT / yr]': f * cn.DDGS.F_mass / 1e3,
              'Crude oil [MT / yr]': f * cn.crude_oil.F_mass / 1e3},
         'Sales':
             {'Ethanol': f * cn.ethanol.cost,
              'DDGS': f * cn.DDGS.cost,
              'Crude oil': f * cn.crude_oil.cost},
         'Utilities':
             {'Electricity': f * sum([i.cost for i in power_utilities]),
              'Steam': f * (sum([i.cost for i in heating_utilities]) + cn.steam.cost),
              'Natural gas': f * cn.D610.natural_gas_cost,
              'Cooling water': f * sum([i.cost for i in cooling_utilities])},
         'Labor and supplies': 
             {'Plant operations': cn.corn_tea.labor_cost * (1. + cn.corn_tea.fringe_benefits + cn.corn_tea.supplies),
              'Maintenance': maintenance},
         'Insurance, property tax, and administration':
             FCI*(cn.corn_tea.property_tax + cn.corn_tea.property_insurance + cn.corn_tea.administration),
         
         'Depreciation': cn.corn_tea.TDC / 10.,
         'Fixed operating cost': FOC,
         'Variable operating cost': cn.corn_tea.VOC,
         'Fixed capital cost': FCI,
         
    }
    sales = dct['Sales']
    dct['Co-product credit'] = credit = - sales['DDGS'] - sales['Crude oil']
    dct['Total production cost'] = x = sum([*dct['Material costs'].values(),
                                        *dct['Utilities'].values(),
                                        dct['Depreciation'],
                                        dct['Co-product credit'],
                                        dct['Fixed operating cost']]) 
    dct['Production cost [USD/gal]'] = x / dct['Production']['Ethanol [MMgal / yr]'] / 1e6
    dct['Operating cost [USD/gal]'] = (x - dct['Depreciation']) / dct['Production']['Ethanol [MMgal / yr]'] / 1e6
    return dct