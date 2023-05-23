# -*- coding: utf-8 -*-
"""
Created on Wed Mar 30 19:05:56 2022

@author: JK
"""

import pandas as pd


cars = pd.read_csv('cars_prices.csv', index_col = 0)

cars.head(5)
cars.describe()
cars.info()

cars.isnull().sum()
cars.drop(columns=['generation_name'], inplace=True)

cars.isnull().sum()

cars['province'].value_counts()
provinces = cars['province'].unique()
cars.drop(cars[cars['province'] == '('].index, inplace=True) 
cars.drop(cars[cars['province'] == 'Berlin'].index, inplace=True) 
cars.drop(cars[cars['province'] == 'Wiedeń'].index, inplace=True) 
cars.drop(cars[cars['province'] == 'Niedersachsen'].index, inplace=True) 
cars.drop(cars[cars['province'] == 'Moravian-Silesian Region'].index, inplace=True)
cars.drop(cars[cars['province'] == 'Trenczyn'].index, inplace=True)
cars.drop(cars[cars['province'] == 'Nordrhein-Westfalen'].index, inplace=True)

provinces = cars['province'].unique()
len(provinces)

cars['mark'].value_counts()
marks = cars['mark'].unique()

cars['fuel'].value_counts()

cars['year'].value_counts()
cars = cars[cars['year']>=1990]

cars.to_csv('cars_clean.csv')

