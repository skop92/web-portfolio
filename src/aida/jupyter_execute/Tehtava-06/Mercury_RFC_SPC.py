#!/usr/bin/env python
# coding: utf-8
---
title: ML test
description: Solar panel classification
show-code: False
params:
    p_year:
        input: range
        label: Set prediction start year
        value: [2018,2019]
        min: 2016
        max: 2019
        step: 1
    t_size:
        input: slider
        label: Set test size
        value: 0.2
        min: 0.1
        max: 0.9
        step: 0.05
    r_state:
        input: slider
        label: Set random state
        value: 5
        min: 0
        max: 10
        step: 1
    n_est:
        input: slider
        label: Set n estimators
        value: 100
        min: 10
        max: 300
        step: 10
    size:
        input: select
        label: Set size
        value: all
        choices: [all,extra small,small,large,extra large]
    rang:
        input: range 
        label: Price per kW range
        value: [170,300]
        min: 170
        max: 1000
        step: 10
---
# In[1]:


p_year = [2018,2019]
t_size = 0.2
r_state = 5
n_est = 100
size = 'all'
rang = [170,400]


# # ML test GUI for Random Forest Classifier
# 
# The purpose of this model is to search for the best-rated models and list a few of the best ones according to the price-size ratio and built-in meter.
# 
# The idea is that the user can search for the best option according to the size required. With the test in mind other options have been included. The model is not ready but a possible prototype.
# 
# * In the year selection you can select the prediction year range
# * You can also test some ML parameters and see how they affect accuracy
# * Size class is default all
# * And last price-size range

# # Results

# In[2]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# Contain also names
url_src = "data/rfc_sample2.csv"
df = pd.read_csv(url_src, parse_dates=True)
# Contain only numeric data
url_src = "data/rfc_model2.csv"
model = pd.read_csv(url_src, parse_dates=True)

# Create tables for both to link names and models
manufacturer = df['module_manufacturer'].value_counts().reset_index()
manufacturer2 = model['module_manufacturer'].value_counts().reset_index()
# mod = module model
mod = df['module_model'].value_counts().reset_index()
mod2 = model['module_model'].value_counts().reset_index()
# Change columns names
manufacturer.columns = ['manufacturer', 'amount']
manufacturer2.columns = ['number', 'amount']
manufacturer['number'] = manufacturer2['number']
mod.columns = ['model', 'amount']
mod2.columns = ['number', 'amount']
# Assing module name df number column
mod['number'] = mod2['number']
unit_name = ['module_manufacturer','module_model']
# Have to drop extra column that was created
df = df.drop(['Unnamed: 0'], axis=1)
model = model.drop(['Unnamed: 0'], axis=1)

# Predictions
pred = model.loc[model['year'].isin(p_year)]
pred = pred.drop(['stars'], axis=1)
print('Prediction legth:',len(pred))
print('_____________________________')
t = t_size
r = r_state
n = n_est
model = model.loc[~model['year'].isin(p_year)]

# This cols are use to teach to the model
ucol = ['total_installed_price','system_size_DC', 'module_manufacturer']
X = model[ucol]
y = model['stars']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = t, random_state= r)
clf = RandomForestClassifier(n_estimators = n) 
clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)
ar_unique, i = np.unique(y_pred, return_counts=True)

# Calculate the absolute errors
errors = abs(y_pred - y_test)
# Print out the mean absolute error (mae)
print('Mean Absolute Error:', round(np.mean(errors), 2), 'degrees.')
# Calculate mean absolute percentage error (MAPE)
mape = 100 * (errors / y_test)

# Calculate and display accuracy
accuracy = 100 - np.mean(mape)
print('Accuracy:', round(accuracy, 5), '%.')
predictions = clf.predict(pred[ucol])

# Assing stars
pred['stars'] = predictions

# Link stars to module
best2 = pred['module_model'].loc[pred.stars == pred.stars.max()].unique()
b2_df = pd.DataFrame(columns=['model','amount','number'])
for b in best2:
    b2_df = pd.concat([b2_df, mod.loc[mod['number'] == b]], axis=0)
    
b2_df = b2_df.sort_values(by='amount',ascending=False).reset_index()    
b2_df = b2_df.drop('index', axis=1)
link_models = df.loc[(df.year.isin(p_year))&(df.module_model != 'Unknown')]

# Create filter list to models
filter_list = b2_df['model'].unique()

# Fecth data by filter list
best = link_models.loc[(link_models['module_model'].isin(filter_list))&(link_models.stars == 3)]
best = best.sort_values(by='p_s')

# Used cols
cols = ['module_manufacturer','module_model','built_in_meter_inverter','efficiency_module','p_s','system_size_DC','RES']
vcountcols = ['module_manufacturer','module_model','built_in_meter_inverter',
                     'efficiency_module','p_s','system_size_DC','RES','count']

# Mean size is used to create size class
mean = best.system_size_DC.mean()

# Function that rewturns wanted size class and prize-size relation range
def get_res(x,ps_rang):
    r = best[cols].loc[(best.p_s > ps_rang[0]) & (best.p_s < ps_rang[1])]
    if x == 'all':
        r = r.value_counts().to_frame().reset_index()
        r.columns = vcountcols
        return r
    if x == 'extra small':
        r = r.loc[r.system_size_DC < r.system_size_DC.mean()]
        r = r.loc[r.system_size_DC < r.system_size_DC.mean()]
        r = r.value_counts().to_frame().reset_index()
        r.columns = vcountcols
        return r.loc[r.system_size_DC < r.system_size_DC.mean()]
    if x == 'small':
        r = r.loc[r.system_size_DC < r.system_size_DC.mean()]
        r = r.loc[r.system_size_DC > r.system_size_DC.mean()]
        r = r.value_counts().to_frame().reset_index()
        r.columns = vcountcols
        return r.loc[r.system_size_DC > r.system_size_DC.mean()]
    if x == 'large':
        r = r.loc[r.system_size_DC > r.system_size_DC.mean()]
        r = r.loc[r.system_size_DC < r.system_size_DC.mean()]
        r = r.value_counts().to_frame().reset_index()
        r.columns = vcountcols
        return r.loc[r.system_size_DC < r.system_size_DC.mean()]
    if x == 'extra large':
        r = r.loc[r.system_size_DC > r.system_size_DC.mean()]
        r = r.loc[r.system_size_DC > r.system_size_DC.mean()]
        r = r.value_counts().to_frame().reset_index()
        r.columns = vcountcols
        return r.loc[r.system_size_DC > r.system_size_DC.mean()]
    
# Function call
res = get_res(size,rang)

# Little result sorting.. p_s = price-size
r1 = res.sort_values(by='p_s').head(4)
r2 = res.sort_values(by='efficiency_module', ascending=False).head(4)
print('_____________________________________')
print('Best',len(r1),'sorted by price size relation')
display(r1)
print('Best',len(r2),'sorted by efficieny')
display(r2)
res2 = res.loc[res.built_in_meter_inverter == 1]

# Additional print to build in meter inverter
if len(r2.loc[r2.built_in_meter_inverter == 1]) < 2:
    r3 = res2.sort_values(by='p_s', ascending=False).head(4)
    print('Best',len(r3),'sorted by price size relation with built in meter inverter')
    display(r3)
    r4 = res2.sort_values(by='efficiency_module', ascending=False).head(4)
    print('Best',len(r4),'sorted by efficieny with built in meter inverter')
    display(r4)


# ## Some thoughts...
# 
# Mercury give you opportunity to parametrize all most everything you want and this is just small scrats for surface. I could  easily paramtrize...
# 
# * How many results are shown
# * If I have plots I could parametrize axis data
# * How many or what cols are shown
# 
# Some cons...
# 
# * You can't publish it free anymore in web.(Heroku isn't free any more)
# * You need to put all most everything in same cell
# 
# After all if you need simple test interface for yourself its quite easy to setup localy and might help also in test and your own data-analysis.

# In[ ]:




