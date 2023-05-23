# -*- coding: utf-8 -*-
"""
Created on Sat Mar 26 17:42:30 2022

@author: JK
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV

np.random.seed(10)

#%%

cars = pd.read_csv("cars_clean.csv")
cars.drop(columns = ["model", "city", "province","Unnamed: 0"], inplace = True)

cars_data = cars.copy()

cars_data.info()
cars_data.isnull().sum()

correlation_cars=cars.corr()


#%%
cars_data = pd.get_dummies(cars_data, drop_first=True)

#%%
#cars_data.to_csv('cars_data.csv')

#%%
X = cars_data.copy()
y = X.pop('price')

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

#%%
lin_model = LinearRegression()
lin_model.fit(X_train, y_train)

lin_model_score = lin_model.score(X_test, y_test)

#%%
reg_model = RandomForestRegressor()
reg_model.fit(X_train, y_train)

reg_model_score = reg_model.score(X_test, y_test)
print(reg_model_score)

#%%
model = RandomForestRegressor()
param_grid = [{'max_depth':[6, 7, 10, 20],
               #'min_samples_leaf': [3,4,5,10],
               'n_estimators': [30, 50, 100, 200, 300],
               #'min_samples_split': [2,3],
               #'max_features': [2,4,6,8,10]
               }]

gs = GridSearchCV(model, param_grid=param_grid, scoring = 'r2')
gs.fit(X_train, y_train)

#%%
gs_score = gs.score(X_test, y_test)
print(gs_score)
print(gs.best_score_)
print(gs.best_params_)

#%%
model = gs.best_estimator_
print(gs.best_estimator_)
#%%

import pickle

with open('cars_model.pickle', 'wb') as file:
    pickle.dump(model, file)






