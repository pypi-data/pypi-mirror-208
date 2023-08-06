# -*- coding: utf-8 -*-
# Bluesteam
# Copyright (C) 2022-, Sarang Bhagwat <sarangb2@illinois.edu>
# 
# This module is under the MIT open-source license. See 
# github.com/BluestemBiosciences/bluesteam/LICENSE.txt
# for license details.
"""
"""
import biosteam as bst
import thermosteam as tmo
from biosteam.units.decorators import cost
from biorefineries.corn import units as corn_units
from biorefineries.corn.units import *

ParallelRxn = tmo.reaction.ParallelReaction

__all__ = (

    'SimultaneousSaccharificationFermentation', 'SSF',
    *corn_units.__all__
)

# @cost('Reactor volume', 'Spargers', CE=521.9, cost=84400,
#       S=1.71e+03, n=0.5, BM=2.3, N='Number of reactors')
# @cost('Reactor volume', 'Reactors', CE=521.9, cost=844000,
#       S=3785, n=0.5, BM=2.3, N='Number of reactors')
class SimultaneousSaccharificationFermentation(bst.BatchBioreactor):
    """
    Create a SimultaneousSaccharificationFermentation unit operation that 
    models the simultaneous saccharification and fermentation in the conventional
    dry-grind ethanol process.
    
    Parameters
    ----------
    ins : streams
        Inlet fluids.
    outs : stream
        Outlet fluid.
    yield_: float
        Yield of glucose to ethanol as a fraction of the theoretical yield.
    
    Notes
    -----
    This unit operation doesn't actually model the saccharification process.
    The reactor is modeled by the stoichiometric conversion of glucose to
    ethanol by mol:
        
    .. math:: 
        Glucose -> 2Ethanol + 2CO_2
    
    Yeast is assumed to be produced from any remaining glucose:
        Glucose -> 6Yeast + 2.34H2O
    
    A compound with name 'Yeast' must be present. Note that only glucose is 
    taken into account for conversion. Cleaning and unloading time,
    `tau_0`, fraction of working volume, `V_wf`, and number of reactors,
    `N_reactors`, are attributes that can be changed. Cost of a reactor
    is based on the NREL batch fermentation tank cost assuming volumetric
    scaling with a 6/10th exponent [1]_. 
    
    References
    ----------
    .. [1] D. Humbird, R. Davis, L. Tao, C. Kinchin, D. Hsu, and A. Aden
        National. Renewable Energy Laboratory Golden, Colorado. P. Schoen,
        J. Lukas, B. Olthof, M. Worley, D. Sexton, and D. Dudgeon. Harris Group
        Inc. Seattle, Washington and Atlanta, Georgia. Process Design and Economics
        for Biochemical Conversion of Lignocellulosic Biomass to Ethanol Dilute-Acid
        Pretreatment and Enzymatic Hydrolysis of Corn Stover. May 2011. Technical
        Report NREL/TP-5100-47764
    
    
    """
    _N_ins = 6
    _N_outs = 2
    
    def __init__(self, ID='', ins=None, outs=(), thermo=None, *, 
                 tau=60.,  N=None, V=None, T=305.15, P=101325., Nmin=2, Nmax=36,
                 yield_=0.95, V_wf=0.83, 
                 aeration_rate=25e-3, # mol/L/h
                 aeration_time=60., # h
                 update_fermentation_performance_based_on_aeration=False,
                 ):
        bst.BatchBioreactor.__init__(self, ID, ins, outs, thermo,
            tau=tau, N=N, V=V, T=T, P=P, Nmin=Nmin, Nmax=Nmax
        )
        self.reactions = ParallelRxn([tmo.Rxn('Glucose -> 2Ethanol + 2CO2',  'Glucose', yield_),
                                     tmo.Rxn('Glucose -> 6Yeast + 2.34H2O',  'Glucose', 1.0-yield_),]) # 7.254 Yeast + 0.174 DAP + 15.63 CSL 
        
        self.reaction = self.reactions[0]
        self.growth = self.reactions[1]
        self.glucose_oxidation = tmo.Rxn('Glucose -> 6CO2 + 6H2O',  'Glucose', 1.0-1e-5) 
        self.V_wf = V_wf
        self.aeration_rate = aeration_rate
        self.aeration_time = aeration_time
        self.update_fermentation_performance_based_on_aeration = update_fermentation_performance_based_on_aeration
        
        self._units['Aeration rate'] = 'mol/L/h'
        
        self.broth_to_load = None
    
    def load_tau(self, tau):
        self.tau = tau
        
    def load_broth(self, bluestream):
        self.broth_to_load = bluestream.stream
        
    def _run(self):
        aeration_rate = self.aeration_rate
        if self.update_fermentation_performance_based_on_aeration:
            self.growth.X, self.reaction.X = self.get_yields_from_aeration_rate(aeration_rate)
        feed, yeast, csl, dap, air, water = self.ins
        self.air = air
        vent, effluent = self.outs
        
        if not self.broth_to_load:
            effluent.mix_from(self.ins[:-1])
            # import pdb
            # pdb.set_trace()
            try:
                air.imol['O2'] = 6.56
                air.imol['N2'] = 28.2
            except:
                air.imol['g','O2'] = 6.56
                air.imol['g','N2'] = 28.2
            air.F_mol = aeration_rate*self.tau*effluent.F_vol*5.29878 * self.aeration_time/self.tau
            self.reactions(effluent)
            # self.growth(effluent)
            # import pdb
            # pdb.set_trace()
            # print(effluent.imol['Glucose'])
            self.glucose_oxidation(effluent)
            effluent.imass['Yeast'] += effluent.imass['NH3']
            effluent.imol['NH3'] = 0.
        
        else:
            effluent.copy_like(self.broth_to_load)
            self.ins[5].imol['Water'] = max(0, sum([i.imol['Water'] for i in self.outs])-sum([i.imol['Water'] for i in self.ins]))
            
        vent.empty()
        vent.receive_vent(effluent)
        
        # vent.receive_vent(air)
        vent.imol['O2'] += air.imol['O2']
        vent.imol['N2'] += air.imol['N2']
        
        effluent.imol['O2'] = 0.
        effluent.imol['N2'] = 0.
        effluent.imol['CO2'] = 0.
        
        dap.imol['DAP'] = 0.012*effluent.imol['Yeast']
        csl.imol['CSL'] = (0.158/0.0725)*effluent.imol['Yeast'] - dap.imol['DAP']*2.
        
        vent.imol['CO2'] += csl.imol['CSL']
        
    @property
    def Hnet(self):
        X = self.reaction.X
        glucose = self.ins[0].imol['Glucose']
        return self.reaction.dH * glucose + self.growth.dH * (1 - X) + self.H_out - self.H_in
    
    def _design(self):
        bst.BatchBioreactor._design(self)    
        Design = self.design_results
        Design['Aeration rate'] = self.aeration_rate
        
    def _cost(self):
        bst.BatchBioreactor._cost(self)
        # self.power_utility(self.get_power())
        self.power_utility.consumption += self.get_power()
    @property
    def yield_(self):
        return self.reaction.X
    @yield_.setter
    def yield_(self, yield_):
        self.reaction.X = yield_
        
    def get_yields_from_aeration_rate(self, aer_rate):
        yeast_yield = 0.27762 + ((aer_rate-0.050)/(0.004-0.050))*(0.1105-0.27762)
        etoh_yield = 0.237 + ((aer_rate-0.050)/(0.004-0.050))*(0.43-0.237)
        return yeast_yield/0.82709, etoh_yield/0.51143
    
    def get_power(self):
        aeration_rate = self.aeration_rate
        aeration_time = self.aeration_time
        tau = self.tau
        air_imass_O2 = self.air.imass['O2']
        effective_aeration_rate = aeration_rate*(aeration_time/tau)
        if effective_aeration_rate>=10e-3:
            return (1.9 + 0.2*(effective_aeration_rate-10e-3))*air_imass_O2 # ~1.9-2.1 kWh/kg-O2 from Humbird et al. 2017
        else:
            cost_at_10_mmol_per_L_per_h = 1.9*air_imass_O2 
            return cost_at_10_mmol_per_L_per_h * (1. - (10e-3-effective_aeration_rate)/10e-3) # linear interpolation; 0 to 1.9 kWh/kg-O2

SSF = SimultaneousSaccharificationFermentation