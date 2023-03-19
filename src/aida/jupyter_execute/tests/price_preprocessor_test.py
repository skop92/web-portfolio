#!/usr/bin/env python
# coding: utf-8

# # TESTI: 'total_installed_price' esikäsittely
# 
# Koodi testaa `preprocessor.py` esikäsittelijän toiminnan sarakkeelle 'total_installed_price'. Testi ajetaan kahdella varsinaisella modella: 'minimal' ja 'common'. Vanha 'stand_alone_PV' on korvattu hyödyntämällä uutta saraketta 'battery_storage', joka ilmaisee akun kuulumista järjestelmään.
# 
# Lisänä huomioitu lähinnä 'Tesla Energy' asennusyrityksen vaikutus 'price_per_kW' välillä [5100, 5200], jossa on hintatehosuhdejakauman korkein piikki.

# ## Mode: 'minimal'

# In[1]:


import pandas as pd
import numpy as np

import importlib.util
import sys
file_path = "../Tehtava-03/preprocessor.py"; module_name = "preprocessor"; spec = importlib.util.spec_from_file_location(module_name, file_path)
esik = importlib.util.module_from_spec(spec); sys.modules[module_name] = esik; spec.loader.exec_module(esik)


cols = ['total_installed_price', 'price_per_kW', 'installer_name', 'battery_storage']

df = esik.esik(cols, 'minimal')
df.describe(percentiles=[.2, .5, .8])


# In[2]:


df = df[(df['price_per_kW'] <= 5200) & (df['price_per_kW'] >= 5100)]
df['installer_name'].value_counts().head(5)


# ## Mode: 'common'

# In[3]:


df = esik.esik(cols, 'common')
df.describe(percentiles=[.2, .5, .8])


# In[4]:


df = df[(df['price_per_kW'] <= 5200) & (df['price_per_kW'] >= 5100)]
df['installer_name'].value_counts().head(5)


# ## Mode: 'stand_alone_PV'
# 
# Tässä tehdään 'stand_alone_PV' suodatus vasta esikäsittelijä funktion jälkeen, koska päivityksen myötä vanha mode poistettiin käytöstä. Uudessa versiossa käytettävä mode on 'common'.

# In[5]:


df = esik.esik(cols, 'common')
df = df[(df['battery_storage'] == 0)]
df.describe(percentiles=[.2, .5, .8])


# In[6]:


df = df[(df['price_per_kW'] <= 5200) & (df['price_per_kW'] >= 5100)]
df['installer_name'].value_counts().head(5)


# ## Mode: 'paired_PV_and_storage'
# 
# Edellisen vastapainoksi vain akkujärjestelmät uutena lisänä.

# In[7]:


df = esik.esik(cols, 'common')
df = df[(df['battery_storage'] == 1)]
df.describe(percentiles=[.2, .5, .8])


# In[8]:


df = df[(df['price_per_kW'] <= 5200) & (df['price_per_kW'] >= 5100)]
df['installer_name'].value_counts().head(5)

