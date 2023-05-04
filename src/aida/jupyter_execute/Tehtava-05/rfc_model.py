#!/usr/bin/env python
# coding: utf-8

# # Random Forest Classifier
# ## Solar panel data

# In[1]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import ipywidgets as widgets
url_src = "data/rfc_sample2.csv"
df = pd.read_csv(url_src, parse_dates=True)
url_src = "data/rfc_model2.csv"
model = pd.read_csv(url_src, parse_dates=True)
manufacturer = df['module_manufacturer'].value_counts().reset_index()
manufacturer2 = model['module_manufacturer'].value_counts().reset_index()
mod = df['module_model'].value_counts().reset_index()
mod2 = model['module_model'].value_counts().reset_index()
manufacturer.columns = ['manufacturer', 'amount']
manufacturer2.columns = ['number', 'amount']
manufacturer['number'] = manufacturer2['number']
mod.columns = ['model', 'amount']
mod2.columns = ['number', 'amount']
mod['number'] = mod2['number']
unit_name = ['module_manufacturer','module_model']
print(manufacturer.shape)
print(mod.shape)
df = df.drop(['Unnamed: 0'], axis=1)
model = model.drop(['Unnamed: 0'], axis=1)


# In[2]:


pred = model.loc[model['year'] >= 2019]
pred = pred.drop(['stars'], axis=1)
len(pred)


# ### This example RFC I chooce to use size, manufacturer and model.

# In[3]:


model = model.loc[model['year'] < 2019]
ucol = ['total_installed_price','system_size_DC', 'module_manufacturer']
X = model[ucol]
y = model['stars']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
clf = RandomForestClassifier(n_estimators = 100) 
clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)
ar_unique, i = np.unique(y_pred, return_counts=True)
# display the returned array
print("Unique values:", ar_unique)
# display the counts
print("Counts:", i)


# In[4]:


model_df = pd.DataFrame({'Actual':y_test, 'Predicted':y_pred})
model_df.value_counts()


# ### If the total installed price is leaved out accuracy drop under 90%

# In[5]:


# Calculate the absolute errors
errors = abs(y_pred - y_test)
# Print out the mean absolute error (mae)
print('Mean Absolute Error:', round(np.mean(errors), 2), 'degrees.')

# Calculate mean absolute percentage error (MAPE)
mape = 100 * (errors / y_test)
# Calculate and display accuracy
accuracy = 100 - np.mean(mape)
print('Accuracy:', round(accuracy, 5), '%.')


# ### Test prediction in 2019 set

# In[6]:


# pred = pred[['module_manufacturer_1','module_model_1','system_size_DC']]
predictions = clf.predict(pred[ucol])
ar_unique, i = np.unique(predictions, return_counts=True)
# display the returned array
print("Unique values:", ar_unique)
# display the counts
print("Counts:", i)


# ### Extra, link data to actual names

# In[7]:


# Assing stars
pred['stars'] = predictions
# Link stars to module
best2 = pred['module_model'].loc[pred.stars == pred.stars.max()].unique()
b2_df = pd.DataFrame(columns=['model','amount','number'])
for b in best2:
    b2_df = pd.concat([b2_df, mod.loc[mod['number'] == b]], axis=0)
b2_df = b2_df.sort_values(by='amount',ascending=False).reset_index()
b2_df = b2_df.drop('index', axis=1)
link_models = df.loc[(df.year == 2019)&(df.module_model != 'Unknown')]
# Create filter list to models
filter_list = b2_df['model'].unique()
# Fecth data by filter list
best = link_models.loc[(link_models['module_model'].isin(filter_list))&(link_models.stars == 3)]
best = best.sort_values(by='p_s')
best[['module_manufacturer','module_model']].value_counts().head(20)


# ### Some thoughts
# * Could it be usefull to buid some function?
# 
# [Link to data preparation](https://temppase.github.io/rfc_preparation/)

# ### Additional features
# * posible function or functions to find other features
# * Further development still under consideration

# In[8]:


s = 'small'
l = 'large'
cols = ['module_manufacturer','module_model','built_in_meter_inverter','efficiency_module','p_s','system_size_DC','RES']
vcountcols = ['module_manufacturer','module_model','built_in_meter_inverter',
                     'efficiency_module','p_s','system_size_DC','RES','count']
mean = best.system_size_DC.mean()
def best_size_class(x,psfloor,psceiling,):
    if x == 'small':
        return best.loc[(best.p_s > int(psfloor))&(best.p_s < int(psceiling))&(best.system_size_DC < mean)]
    if x == 'large':
        return best.loc[(best.p_s > int(psfloor))&(best.p_s < int(psceiling))&(best.system_size_DC > mean)]


# ### Extra small

# In[9]:


# Small
small = best_size_class(s,0,500)
small = small[cols].value_counts().to_frame().reset_index()
small.columns = vcountcols
extra_small = small.loc[small.system_size_DC < small.system_size_DC.mean()]
small = small.loc[small.system_size_DC > small.system_size_DC.mean()]
extra_small


# ### Small

# In[10]:


small


# ### Large

# In[11]:


# Large
large = best_size_class(l,0,500)
large = large[cols].value_counts().to_frame().reset_index()
large.columns = vcountcols
extra_large = large.loc[large.system_size_DC > large.system_size_DC.mean()]
large = large.loc[large.system_size_DC < large.system_size_DC.mean()]
large


# ### Extra large

# In[12]:


extra_large


# ### Notifications
# * Larger the system size -> smaller the price/kW also high efficieny rise price/kW. Some exeptions will be found.

# In[ ]:




