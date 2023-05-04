#!/usr/bin/env python
# coding: utf-8

# # TESTI: 'system_size_DC' esikäsittely
# 
# Koodi testaa `preprocessor.py` esikäsittelijän toiminnan sarakkeelle 'system_size_DC'.
# 
# Testi ajetaan kahdella modella: 'minimal' ja 'common'.
# 
# - 'minimal' ei tee mitään.
# - 'common' karsii datasta sellaiset 'system_size_DC':n arvot, jotka eivät ole riittävän lähellä laskennalla tarkistettua arvoa.
# 
# Testiin on myös lisätty sarakkeet 'year' ja 'price_per_W', koska ne lisättiin samaan aikaan.
# 
# ## Mode: 'minimal'

# In[1]:


import importlib.util
import sys
file_path = "../Tehtava-03/preprocessor.py"; module_name = "preprocessor"; spec = importlib.util.spec_from_file_location(module_name, file_path)
esik = importlib.util.module_from_spec(spec); sys.modules[module_name] = esik; spec.loader.exec_module(esik)

cols = ['system_size_DC', 'year', 'price_per_W']

df_all = esik.esik(cols, 'minimal')

# Printit
print("df_all.shape:", df_all.shape)
display(df_all.groupby(['year']).agg({'system_size_DC': ['size', 'count'], 'price_per_W': ['size', 'count', 'max']}))
df_all.describe(percentiles=[.2, .5, .8])


# ## Mode: 'common'
# 
# Testiajo oletusarvoilla. Oletus-mode: 'common'.

# In[2]:


df_all = esik.esik(cols)

print("df_all.shape:", df_all.shape)
display(df_all.groupby(['year']).agg({'system_size_DC': ['size', 'count'], 'price_per_W': ['size', 'count', 'max']}))
df_all.describe(percentiles=[.2, .5, .8])


# ### 'unchecked_sizes' test
# 
# Testataan parametrin `unchecked_sizes` toiminta. Parametrin oletusarvo on `False`.

# In[3]:


df_all = esik.esik(cols, unchecked_sizes=True)

print("df_all.shape:", df_all.shape)
display(df_all.groupby(['year']).agg({'system_size_DC': ['size', 'count'], 'price_per_W': ['size', 'count', 'max']}))
df_all.describe(percentiles=[.2, .5, .8])

