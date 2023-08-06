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
from matplotlib import pyplot as plt
import biosteam as bst
from biosteam import BinaryDistillation, ShortcutColumn, Flash
import thermosteam as tmo
from thermosteam import Chemical, Stream
import pandas as pd
from pandas import DataFrame
# from biorefineries.succinic.analyses.solvents_barrage import run_solvents_barrage
from warnings import filterwarnings
filterwarnings('ignore')

#%% Utils

class BlueStream:
    def __init__(self,composition_dict,
                 products,
                 impurities,
                 ID=None):
        chems = []
        if not ID:
            ID = f's_{int(1e6*round(np.random.rand(), 6))}'
        for k in composition_dict.keys():
            if type(k)==str:
                chems.append(Chemical(k))
            else:
                chems.append(k)
        tmo.settings.set_thermo(chems)
        self.ID = ID
        self.stream = stream = Stream(ID=ID)
        for k, v in composition_dict.items():
            if type(k)==str:
                stream.imol[k] = v
            else:
                stream.imol[k.ID] = v
        
        self.products = products
        self.impurities = impurities
    
    def __repr__(self):
        self.stream.show('cmol100')
        return f''
    

class SequentialDistillationResult:
    def __init__(self, result):
        self.stream = result[0][0]
        self.products = result[0][1]
        self.impurities = result[0][2]
        self.score = result[1]
        self.columns = result[2]
        self.azeotropes = result[3]
        self.exceptions = []
        
    def __repr__(self):
        return f'\nSequentialDistillationResult\nStream: {self.stream.ID}\nProducts: {self.products}\nImpurities: {self.impurities}\nAzeotropic key pairs ({len(self.azeotropes)} total): {self.azeotropes}\nExceptions: {self.exceptions}\nScore: {self.score}\n'

get_heating_demand = lambda unit: sum([i.duty for i in unit.heat_utilities if i.duty*i.flow>0])

def get_vle_components_sorted(stream, cutoff_Z_mol=1e-3):
    # vle_chemicals = stream.vle_chemicals
    sorted_list = list([i for i in stream.vle_chemicals if stream.imol[i.ID]/stream.F_mol>cutoff_Z_mol])
    sorted_list.sort(key=lambda i: i.Tb if i.Tb else np.inf)
    return sorted_list

def add_flash_vessel(in_stream,
                    V, 
                    ID=None,
                    P=101325., 
                    vessel_material='Stainless steel 316',
                    ):
    if not ID:
        ID=f'{in_stream.ID}_Flash'
    return Flash(ID, ins=in_stream, outs=(f'{ID}_0', f'{ID}_1'), 
                     V=V, 
                     P=P)

def add_distillation_column(in_stream,
                            LHK, 
                            Lr, Hr,
                            column_type='BinaryDistillation',
                            ID=None,
                            k=1.05, P=101325., 
                            is_divided=True,
                            partial_condenser=False,
                            vessel_material='Stainless steel 316',
                            ):
    if not ID:
        ID=f'{in_stream.ID}_{column_type}'
    new_column = None
    if column_type =='BinaryDistillation':
        new_column = BinaryDistillation(ID, ins=in_stream, outs=(f'{ID}_0', f'{ID}_1'),
                                            LHK=LHK,
                                            is_divided=is_divided,
                                            product_specification_format='Recovery',
                                            Lr=Lr, Hr=Hr, k=k, P=P,
                                            vessel_material=vessel_material,
                                            partial_condenser=partial_condenser,
                                            # condenser_thermo = ideal_thermo,
                                            # boiler_thermo = ideal_thermo,
                                            # thermo=ideal_thermo,
                                            )
    elif column_type =='ShortcutColumn':
        new_column = ShortcutColumn(ID, ins=in_stream, outs=(f'{ID}_0', f'{ID}_1'),
                                            LHK=LHK,
                                            is_divided=is_divided,
                                            product_specification_format='Recovery',
                                            Lr=Lr, Hr=Hr, k=k, P=P,
                                            vessel_material=vessel_material,
                                            partial_condenser=partial_condenser,
                                            # condenser_thermo = ideal_thermo,
                                            # boiler_thermo = ideal_thermo,
                                            # thermo=ideal_thermo,
                                            )
    return new_column

def get_sinkless_streams(units, p_chem_IDs):
    ss = []
    for u in units:
        for s in u.outs:
            if not s.sink:
                # print(1)
                if not is_a_product_stream(s, p_chem_IDs)\
                    and not is_a_productless_stream(s, p_chem_IDs):
                        # print(11)
                    ss.append(s)
    return ss

def is_a_product_stream(stream, p_chem_IDs, min_purity=0.8):
    return np.any(np.array([stream.imol[c]/stream.F_mol >= min_purity for c in p_chem_IDs]))
        
def is_a_productless_stream(stream, p_chem_IDs, cutoff_Z_mol=0.2):
    return not np.any(np.array([stream.imol[c]/stream.F_mol >= cutoff_Z_mol for c in p_chem_IDs]))
          
def run_sequential_distillation(stream, products, impurities, 
                                      cutoff_Z_mol=1e-3,
                                score_offset_per_azeotrope=1e9):
    # chemicals = get_thermo().chemicals
    chemicals = stream.chemicals
    tmo.settings.set_thermo(chemicals)
    p_chems = [chemicals[p] for p in products if type(p)==str]
    p_chem_IDs = [pc.ID for pc in p_chems]
    i_chems = [chemicals[i] for i in impurities if type(i)==str]
    i_chem_IDs = [ic.ID for ic in i_chems]
    sorted_chems = get_vle_components_sorted(stream, 1e-3)
    columns = []
    transient_sinkless_streams = [stream]
    azeotropes = []
    try:
        while transient_sinkless_streams:
            # print(transient_sinkless_streams)
            for s in transient_sinkless_streams:
                sorted_chems = get_vle_components_sorted(s, 1e-3)
                LHK=tuple([i.ID for i in sorted_chems[:2]])
                # print(LHK)
                # s.show()
                try:
                    try:
                        new_col = add_distillation_column(in_stream=s,
                                                          LHK=LHK,
                                                          Lr=0.99999, Hr=0.99999,
                                                          P=101325./100,
                                                          column_type ='BinaryDistillation'
                                                          )
                        new_col.simulate()
                        columns.append(new_col)
                    except:
                        try:
                            new_col = add_distillation_column(in_stream=s,
                                                              LHK=LHK,
                                                              Lr=0.99999, Hr=0.99999,
                                                              P=101325./10,
                                                              column_type ='BinaryDistillation'
                                                              )
                            new_col.simulate()
                            columns.append(new_col)
                        except Exception as e:
                            if 'heating agent' in str(e):
                                new_col = add_flash_vessel(in_stream=s,
                                                           V=s.imol[LHK[0]]/sum([s.imol[s_chem.ID] for s_chem in s.vle_chemicals]),
                                                           P=101325./10,
                                                           )
                                new_col.simulate()
                                columns.append(new_col)
                            else:
                                raise e
                except:
                    try:
                        new_col = add_distillation_column(in_stream=s,
                                                          LHK=LHK,
                                                          Lr=0.99999, Hr=0.99999,
                                                          P=101325./100,
                                                          column_type ='ShortcutColumn'
                                                          )
                        new_col.simulate()
                        columns.append(new_col)
                        azeotropes.append(LHK)
                    except:
                        new_col = add_distillation_column(in_stream=s,
                                                          LHK=LHK,
                                                          Lr=0.99999, Hr=0.99999,
                                                          P=101325./10,
                                                          column_type ='ShortcutColumn'
                                                          )
                        new_col.simulate()
                        columns.append(new_col)
                        azeotropes.append(LHK)
            transient_sinkless_streams.clear()
            transient_sinkless_streams += get_sinkless_streams(columns, p_chem_IDs)
            # print(transient_sinkless_streams)
        
        score = sum(get_heating_demand(col) for col in columns)/sum([stream.imol[pci] for pci in p_chem_IDs])
        score += score_offset_per_azeotrope*len(azeotropes)
        return SequentialDistillationResult(result=((stream, p_chem_IDs, i_chem_IDs), score, columns, azeotropes))
    except Exception as e:
        result = SequentialDistillationResult(result=((stream, p_chem_IDs, i_chem_IDs), np.inf, [bst.Unit('EmptyUnit')], []))
        result.exceptions.append(e)
        return result
    
def get_sorted_results(streams, print_results=False, file_to_save=None):
    results = [run_sequential_distillation(stream.stream, stream.products, stream.impurities)
               for stream in streams]
    results.sort(key=lambda r: r.score)
    if print_results:
        for r in results:
            print(r)
    if file_to_save:
        compiled_results_dict = {}
        for result in results:
            compiled_results_dict[result.stream.ID] = rn = {}
            # rn['Stream ID'] = result.stream.ID
            rn['Products'] = [k if type(k)==str else k.ID for k in result.products]
            rn['Impurities'] = [k if type(k)==str else k.ID for k in result.impurities]
            rn['Azeotropic key pairs'] = result.azeotropes
            rn['Number of azeotropes'] = len(result.azeotropes)
            rn['Score'] = result.score
            
        results_df = DataFrame(compiled_results_dict)
        # results_df.to_excel(file_to_save+'.xlsx')
        map_dict = {0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E', 5: 'F', 6: 'G', 7: 'H', 8: 'I', 
        9: 'J', 10: 'K', 11: 'L', 12: 'M', 13: 'N', 14: 'O', 15: 'P', 16: 'Q', 
        17: 'R', 18: 'S', 19: 'T', 20: 'U', 21: 'V', 22: 'W', 23: 'X', 24: 'Y', 25: 'Z'}
        
        final_results_df = None
        with pd.ExcelWriter(file_to_save+'.xlsx') as writer:
            final_results_df = results_df.transpose()
            final_results_df.to_excel(writer, sheet_name='All results')
            workbook  = writer.book
            worksheet = writer.sheets['All results']
            # wrap_format = workbook.add_format({'text_wrap': True})
            # worksheet.set_column('A:A', None, wrap_format)
            # worksheet.set_row('A:A', None, wrap_format)
            # writer.save()
            # Add a header format.
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                # 'fg_color': '#D7E4BC',
                'border': 1})
            decimal_2_format = workbook.add_format({'num_format': '#,##0.00'})
            decimal_3_format = workbook.add_format({'num_format': '#,##0.000'})
            worksheet.set_column('A:A', 18, decimal_2_format)
            
            # Write all cells in the specified number format.
            for i in range(len(final_results_df.columns.values)):
                worksheet.set_column(map_dict[i+1]+':'+map_dict[i+1], 18, decimal_2_format)
            # worksheet.set_row(0, 28, decimal_2_format)
            
            worksheet.write(0,0, 'Stream ID', header_format)
            # Write the column headers with the defined format.
            for col_num, value in enumerate(final_results_df.columns.values):
                worksheet.write(0, col_num + 1, value, header_format)
            # Write the row headers with the defined format.
            for row_num, value in enumerate(final_results_df.index.values):
                worksheet.write(row_num + 1, 0, value, header_format)
            
    return results
