#!/usr/bin/env python
# coding: utf-8

# # TESTI: itse määriteltyjä sarakkeita esikäsittelijällä
# 
# Tässä testissä testataan osaa itse määritellyistä sarakkeista, jotka myös esikäsittelijä osaa luoda. Lisäksi testataan uutta mode-valikoimaa, joka on nyt `['none', 'minimal', 'common']`.
# 
# ## Mode: 'common'
# 
# 'common' on oletus, joten sitä ei välttämättä tarvitse antaa kutsun parametriksi. Mode pyrkii karsimaan virheellisen datan pois ja tekee kaikki pyydetyt itse määritellyt sarakkeet. Tässä testataan:
# 
# - 'customer_segment_3'
#   - Jako: RES, SMALL NON-RES, LARGE NON-RES
#   - NON-RES koostettu alkuperäisistä ryhmistä COM, GOV, SCHOOL, NON-PROFIT, NON-RES
#   - Raja määritellään parametrilla `large-limit`, joka on oletuksena 100 kW
#   - Raja-arvo kuuluu ryhmään 'SMALL NON-RES'
# - 'battery_storage'
#   - bool sarake
#   - arvo 1 : järjestelmässä (arviolta) on akku
#   - arvo 0 : järjestelmässä (arviolta) ei ole akkua
#   - arvioon voi sisällyttää teslan asennuksia kolmella tavalla
#     - 'none' asettaa kaikkiin arvon 0
#     - 'neutral' antaa akun määräytyä muiden kriteerien perusteella
#     - 'all' asettaa kaikkiin arvon 1

# In[1]:


import importlib.util
import sys
file_path = "../Tehtava-03/preprocessor.py"; module_name = "preprocessor"; spec = importlib.util.spec_from_file_location(module_name, file_path)
esik = importlib.util.module_from_spec(spec); sys.modules[module_name] = esik; spec.loader.exec_module(esik)

cols = ['customer_segment_3', 'system_size_DC', 'battery_storage', 'installer_name']

df_none = esik.esik(cols, large_limit=120, tesla_battery='none')
df_neutral = esik.esik(cols, large_limit=120, tesla_battery='neutral', sshi_with_battery=False)
df_all = esik.esik(cols, large_limit=120, tesla_battery='all')


# In[2]:


print("df_all.shape:", df_all.shape)
display(df_all.describe())
display(df_all.groupby(['customer_segment_3']).agg({'system_size_DC': ['size', 'count', 'min', 'max'], 'battery_storage': ['count', 'mean']}))
display(df_all.groupby(['battery_storage']).agg({'system_size_DC': ['size', 'count', 'min', 'max']}))


# ### Akut Tesla Energyllä

# In[3]:


df = df_none.copy()
df = df[(df['battery_storage'] == 1) & (df['installer_name'] == 'Tesla Energy')]
print("df_none.shape: ", df.shape)
df = df_neutral.copy()
df = df[(df['battery_storage'] == 1) & (df['installer_name'] == 'Tesla Energy')]
print("df_neutral.shape: ", df.shape)
df = df_all.copy()
df = df[(df['battery_storage'] == 1) & (df['installer_name'] == 'Tesla Energy')]
print("df_all.shape: ", df.shape)
# sshi_battery True
# 0
# 4808
# 170110


# ## Mode: 'none'
# 
# ### Itse määriteltyjä sarakkeita
# 
# Kielletään varsinainen esikäsittely, mutta yritetään ladata itse määriteltyjä sarakkeita. Pitäisi tulostaa huomautuksen ja ladata vain alkuperäisiin kuuluvat sarakkeet.

# In[4]:


cols = ['customer_segment_3', 'system_size_DC', 'battery_storage']
df_all = esik.esik(cols, 'none')
print("df_all.shape:", df_all.shape)
display(df_all.describe())


# ### Vain alkuperäisiä sarakkeita
# 
# Testataan, että mode toimii myös oikein käytettynä.

# In[5]:


cols = ['total_installed_price', 'system_size_DC']
df_all = esik.esik(cols, 'none')
print("df_all.shape:", df_all.shape)
display(df_all.describe())

