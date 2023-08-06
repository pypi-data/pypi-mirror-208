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

from setuptools import setup

setup(
    name='bluesteam',
    packages=['bluesteam'],
    version='0.0.6',    
    description='Bluestem leverages AutoSynthesis, BioSTEAM, and biorefineries in BioIndustrial-Park for automated process synthesis and design of biorefineries.',
    url='https://github.com/BluestemBiosciences/bluesteam',
    author='Sarang S. Bhagwat',
    author_email='sarang.bhagwat.git@gmail.com',
    license='MIT',
    install_requires=[
                      'biorefineries==2.23.18',   
                      'autosynthesis==0.0.17',
                      ],
    package_data=
        {'bluesteam': ['bluesteam_biorefineries/*',
                      'separability_tools/*',
		      'bluesteam_biorefineries/generic/*'
                      ]},
   
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: University of Illinois/NCSA Open Source License',  
        'Operating System :: Microsoft :: Windows',        
        'Programming Language :: Python :: 3.9'
    ],
)
