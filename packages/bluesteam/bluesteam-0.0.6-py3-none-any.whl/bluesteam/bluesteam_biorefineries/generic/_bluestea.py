# -*- coding: utf-8 -*-
# Bluesteam
# Copyright (C) 2022-, Sarang Bhagwat <sarangb2@illinois.edu>
# 
# This module is under the MIT open-source license. See 
# github.com/BluestemBiosciences/bluesteam/LICENSE.txt
# for license details.
"""
"""
from bluesteam.bluesteam_biorefineries.generic._tea import create_tea
from bluesteam.bluesteam_biorefineries.generic.load_generic import load_set_and_get_upstream_sys
from biosteam import System, SolidsCentrifuge, StorageTank, report
from autosynthesis.utils import get_separation_units
from autosynthesis.solvents_barrage import solvent_IDs
import os

solvent_prices = {solvent: 5. for solvent in solvent_IDs} # solvent price defaults to $5/kg
__all__=['BluesTEA',]

class BluesTEA():
    
    _kmol_glucose_per_wet_kg_corn = 0.0037631783772848998
    _kmol_glucose_per_wet_kg_sucrose = 0.005550744909966918
    
    
    def __init__(self, 
            system_ID = 'sys1',
               IRR=0.15, # 
               duration=(2018, 2038),
               depreciation='MACRS7', income_tax=0.35,
               operating_days=330, lang_factor=4,
               construction_schedule=(0.4, 0.6), WC_over_FCI=0.05,
               labor_cost=2.3e6, fringe_benefits=0.4,
               property_tax=0.001, property_insurance=0.005,
               supplies=0.20, maintenance=0.01, administration=0.005,
               upstream_feed='corn', 
               # upstream_feed_price=0.287, # Singh et al. 2022
               upstream_feed_price=None,
               upstream_feed_capacity=None,# units: determined by upstream_feed_capacity_units
               upstream_feed_capacity_units='kmol-Glucose-eq/h', # 'MT/d', 'kmol-Glucose-eq/h'
               products_and_purities={'AdipicAcid':0.995,}, # {'product ID': purity in weight%}
               products_and_market_prices={'AdipicAcid':4.088}, # {'product ID': price in $/pure-kg}
               aeration_rate=0.,
               aeration_time=100.,
               current_equipment={'R302':('FermentationTank', 20), 
                                  '':()}, # {'unit ID':('unit type', equipment size in m^3)}
               # fermentation_specifications={'Microbe':'Yeast', 'Titer':80, # g/L
               #                              'Productivity': 1, # g/L/h
               #                              'Yield':0.8 # %theoretical
               #                              },
               fermentation_residence_time=100., # h
               bluestream=None, # broth output from fermentation, including microbe
               add_storage_units=True,
               add_upstream_impurities_to_bluestream=False,
               solvent_prices=solvent_prices # format is {ID: price in $/kg}
               ):
        
        self.system_ID = system_ID
        # self.products = bluestream.products
        self.products = {}
        self.bluestream = bluestream
        self.solvent_prices = solvent_prices
        if upstream_feed_capacity:
            if upstream_feed_capacity_units=='kmol-Glucose-eq/h':
                if upstream_feed == 'corn':
                    upstream_feed_capacity /= self._kmol_glucose_per_wet_kg_corn
                elif upstream_feed == 'sucrose':
                    upstream_feed_capacity /= self._kmol_glucose_per_wet_kg_sucrose
            elif upstream_feed_capacity_units == 'MT/d':
                upstream_feed_capacity*=1000/24 # kg/h
        self.system_up_to_fermentation = system_up_to_fermentation =\
            load_set_and_get_upstream_sys(ID=system_ID+'_conversion',
                                                bluestream=bluestream, 
                                                fermentation_tau=fermentation_residence_time,
                                                aeration_rate = aeration_rate,
                                                aeration_time = aeration_time,
                                                upstream_feed=upstream_feed, 
                                                upstream_feed_capacity=upstream_feed_capacity,
                                                )
        
        self.system = system = system_up_to_fermentation
        self.flowsheet = flowsheet = system.flowsheet
        self.fermentation_reactor = fermentation_reactor = flowsheet('V405')
        # fermentation_reactor.show(N=100)
        self.stream_to_separation = fermentation_reactor.outs[1].sink.outs[0]
        self.separation_system = separation_system = self.get_system_from_APD(new_ID=system_ID+'separation')
        
        self.products_and_purities = products_and_purities
        self.products_and_market_prices = products_and_market_prices
        
        self.storage_units = []
        self.set_product_streams_and_prices(add_storage_units=add_storage_units)
        
        
        self.system = system = self.join_systems(system_up_to_fermentation, separation_system, new_ID=system_ID)
        
        self.tea = tea = create_tea(system, 
                   IRR=IRR,
                   duration=duration,
                   depreciation=depreciation, income_tax=income_tax,
                   operating_days=operating_days, lang_factor=lang_factor,
                   construction_schedule=construction_schedule, WC_over_FCI=WC_over_FCI,
                   labor_cost=labor_cost, fringe_benefits=fringe_benefits,
                   property_tax=property_tax, property_insurance=property_insurance,
                   supplies=supplies, maintenance=maintenance, administration=administration)
        
        self.upstream_feed = upstream_feed
        self.upstream_feed_price = upstream_feed_price
        
        self.aeration_rate = aeration_rate
        
        
        # tea_dir = self.tea.__dir__()
        # for i in tea_dir:
        #     if not i in self.__dict__.keys():
        #         self.__dict__[i] = tea.__getattribute__(i)
        self.feedstock = feedstock = flowsheet(upstream_feed)
        # if upstream_feed_capacity:
        #     feedstock.F_mass = upstream_feed_capacity * 1000. / 24.
        if upstream_feed_price:
            feedstock.price = upstream_feed_price
        # print('Simulating\n\n')
        
        # system.simulate()
        
        # for i in range(5):
        #     tea.IRR = tea.solve_IRR()
        
        self.fermentation_reactor.simulate()
        
        self.sys_ferm_sep_storage_only = sys_ferm_sep_storage_only=\
            System.from_units(ID='sys_ferm_sep_storage_only', 
                              units=list([fermentation_reactor, fermentation_reactor.outs[1].sink])+list(separation_system.units)+list(self.storage_units))
        
        # fermentation_reactor.simulate()
        
    def get_system_from_APD(self, new_ID, resimulate=False):
        S401 = SolidsCentrifuge('S401', ins=self.stream_to_separation, 
                                outs=('S401_solid_waste', 'S401_1'),
                                solids=['Yeast'], split={'Yeast':1-1e-4})
        S401.simulate()
        APD_units = get_separation_units(stream=S401-1, products=list(self.bluestream.products), print_progress=False, plot_graph=False,
                                         solvent_prices=self.solvent_prices)
        new_sys = System.from_units(ID=new_ID, units=[S401]+list(APD_units))
        if resimulate:
            new_sys.simulate()
        return new_sys
    
    def join_systems(self, sys1, sys2, new_ID, simulate=True,):
        
        new_sys = System.from_units(ID=new_ID, units=list(sys1.units)+list(sys2.units)+list(self.storage_units))
        if simulate:
            # new_sys.simulate()
            pass
        return new_sys
    
    def save_report(self, filename):
        self.system.save_report(filename)
    
    def set_product_streams_and_prices(self, add_storage_units=True):
        products_and_purities = self.products_and_purities
        products_and_market_prices = self.products_and_market_prices
        
        TEA_product_streams = list(self.separation_system.products) + list(self.system_up_to_fermentation.products)
        
        self.storage_units = storage_units = []
        for ID,p in products_and_purities.items():
            for s in TEA_product_streams:
                s_imass_ID, s_F_mass = s.imass[ID], s.F_mass
                if s_imass_ID/s_F_mass >= p:
                    # print(products_and_market_prices[ID], s_imass_ID, s_F_mass)
                    
                    if add_storage_units:
                        new_storage_unit = StorageTank(ID=ID+'_tank', ins=s, outs=(ID,), tau=7*24)
                        new_storage_unit.simulate()
                        new_storage_unit.outs[0].price = products_and_market_prices[ID]*s_imass_ID/s_F_mass
                        self.products[ID] = new_storage_unit.outs[0]
                        storage_units.append(new_storage_unit)
                    else:
                        s.price = products_and_market_prices[ID]*s_imass_ID/s_F_mass
                        self.products[ID] = s
                        s.ID = ID
        self.storage_units = storage_units
    
    def solve_price(self, product_ID, IRR=0.15, set_as_current_price=False, set_as_current_IRR=False):
        curr_IRR = float(self.tea.IRR)
        self.tea.IRR = IRR
        products = self.products
        product_stream = products[product_ID]
        price = self.tea.solve_price(product_stream)
        if set_as_current_price:
            product_stream.price = price
        if not set_as_current_IRR:
            self.tea.IRR = curr_IRR
        return price
    
    def set_upstream_feed_capacity(self, capacity): # metric tonne/ d
        new_capacity = capacity*1000./24.
        self.stream_to_separation.F_mass *= new_capacity/self.feedstock.F_mass
        self.fermentation_reactor.broth_to_load = self.stream_to_separation
        self.feedstock.F_mass = new_capacity
        self.system.simulate()
        
    def check_mass_balance(self):
        return sum(self.fermentation_reactor.mass_in) - sum(self.fermentation_reactor.mass_out)
    
    def unit_result_tables(self):
        return report.unit_result_tables(self.system.units)
    
    def cost_table(self):
        return report.cost_table(self.tea)
    
    def cashflow_table(self):
        return self.tea.get_cashflow_table()
    
    def save_diagram(self, kind='thorough', system='full', filename=None, format_='png'):
        if not filename:
            filename = 'flowsheet_'+str(self.system_ID)
        diag_sys = None
        if system=='full':
            diag_sys = self.system
        elif system=='ferm_sep_storage_only':
            diag_sys = self.sys_ferm_sep_storage_only
        
        diag_sys.diagram(kind=kind, file=filename, format=format_)
        
    def get_diagram_bytearray(self, kind='thorough', system='ferm_sep_storage_only', filename=None, format_='png'):
        if not filename:
            filename='temp_flowsheet_'+str(self.system_ID)
        self.save_diagram(kind, system, filename, format_)
        b = None
        with open(filename+"."+format_, "rb") as image:
          f = image.read()
          b = bytearray(f)
        os.remove(filename+"."+format_)
        return b
    
    def sep_sys_unit_result_tables(self):
        return report.unit_result_tables(self.separation_system.units)
    
    def set_financing_payoff_years(self, payoff_years): # integer
        self.tea.finance_years = payoff_years
    
    def set_financing_interest_rate(self, interest_rate): # fraction
        self.tea.finance_interest = interest_rate
        
    def add_financing(self, amount=0., unit_fraction_dict={}): # provide an amount of funding to be added at project start 
    # and/or a dictionary with keys as IDs of units of which the installed cost is to to be discounted 
    # and values as discount fraction 
        tea = self.tea
        FCI = tea.FCI
        tea.finance_fraction += amount/FCI
        for unit_ID, fraction in unit_fraction_dict.items():
            tea.finance_fraction += fraction*self.flowsheet(unit_ID).installed_cost/FCI
    
    def get_material_cost_breakdown(self):
        op_hours = self.tea.operating_hours
        return {i.ID: i.cost * op_hours for i in self.system.feeds if i.price}