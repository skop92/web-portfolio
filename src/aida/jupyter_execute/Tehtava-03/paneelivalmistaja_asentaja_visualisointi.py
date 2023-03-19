#!/usr/bin/env python
# coding: utf-8

# # Kuinka pitkään paneelivalmistajat ja asennusfirmat ovat toimineet alalla?

# 
# Paneelin valmistajan ja asentajan ensimmäisen tehtävän päivämäärä.
# 
# 

# In[1]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# Ladataan data tiedostosta ja muutetaan '-9999' NaN:eiksi
url_src = "d:/aidaprojekti\LBNL_file.csv"
df = pd.read_csv(url_src, low_memory=False, na_values = '-9999')

# Muutetaan päivämäärät ja järjestetään sen mukaan
df['installation_date'] = pd.to_datetime(df['installation_date'])
df = df.sort_values(['installation_date'], ascending=True)


# Muutetaan nimet/kirjaimet isoiksi
df['module_manufacturer_1'] = df['module_manufacturer_1'].str.upper()
df['module_manufacturer_2'] = df['module_manufacturer_2'].str.upper()
df['module_manufacturer_3'] = df['module_manufacturer_3'].str.upper()
df['installer_name'] = df['installer_name'].str.upper()


# Otetaan jokainen tarvittava sarake ja päivämäärä
mod1 = df[['installation_date','module_manufacturer_1']]
mod2 = df[['installation_date','module_manufacturer_2']]
mod3 = df[['installation_date','module_manufacturer_3']]
inst = df[['installation_date','installer_name']]


# NaN:it pois
mod11 = mod1.dropna()
mod12 = mod2.dropna()
mod13 = mod3.dropna()
inst1 = inst.dropna()


# paneelin tekijän ja asentajan duplikaatit pois ja aikaisin päivämäärä mukaan
mod11 = mod11.drop_duplicates(subset=['module_manufacturer_1'])
mod12 = mod12.drop_duplicates(subset=['module_manufacturer_2'])
mod13 = mod13.drop_duplicates(subset=['module_manufacturer_3'])
inst1 = inst1.drop_duplicates(subset=['installer_name'])




# Printataan 'module_manufacturer_1' päivämäärän mukaan, josta poistettu dublikaatit.
# 
# Paneeli valmistajien määrä on 317.

# In[2]:


print(mod11)


# Printataan 'module_manufacturer_2' päivämäärän mukaan, josta poistettu dublikaatit.
# 
# Paneeli valmistajien määrä on 154.

# In[3]:


print(mod12)


# Printataan 'module_manufacturer_3' päivämäärän mukaan, josta poistettu dublikaatit.
# 
# Paneeli valmistajien määrä on 72.

# In[4]:


print(mod13)


# Printataan 'installer_name' päivämäärän mukaan, josta poistettu dublikaatit.
# 
# Paneelienasentajien määrä on 4741.

# In[5]:


print(inst1)


# Muutetaan paneelien valmistajat (sarakkeet 1,2,3) samaan sarakkeeseen 'module'.
# Poistetaan dublikaatit

# In[6]:


# Muutetaan module_manufacturer sarakkeiden nimet module:ksi
mod11[['installation_date','module']] = mod11[['installation_date','module_manufacturer_1']]
mod12[['installation_date','module']] = mod12[['installation_date','module_manufacturer_2']]
mod13[['installation_date','module']] = mod13[['installation_date','module_manufacturer_3']]

# Yhdistetään
modul1 = pd.concat([mod11[['installation_date','module']], mod12[['installation_date','module']], mod13[['installation_date','module']]],ignore_index=True)

# Päivämäärän mukaan sortattu
module = modul1.sort_values(['installation_date'], ascending=True)

# poistetaan duplikaatit
modulee = module.drop_duplicates(subset=['module'])



# Printataan yhdistetty paneeli valmistajat päivämäärän mukaan.
# 
# Paneeli valmistajien määrä on kaiken kaikkiaan 321.

# In[7]:


print("modulee::",modulee)


# Printataan paneeli valmistajien mukaan järjestetty.

# In[8]:


# paneelivalmistajan mukaan sortattu vain printtauksen takia
module1 = modulee.sort_values(['module'], ascending=True)
print("moduleee: ",module1)


# 
# 
# Visualisointi 'uusia Paneeli valmistajia / vuosi'.
# 
# Kuvaajasta näkee miten uusia paneelien valmistajia on tullut markkinoille.
# 1998 - 2008 on ollut vain muutama uusi tullut vuodessa.
# Sen jälkeen on valmistajien määrä noussut moninkertaiseksi per vuosi.

# In[9]:


# VISUAALISOINTI 
# paneelivalmistaja: muutetaan vuosiksi ja sen mukaan sortattu
module1['installation_date'] = pd.to_datetime(module1['installation_date'], format='%d-%b-%Y %H:%M:%S') 
module1['installation_date'] = module1['installation_date'].dt.year
module1 = module1.sort_values(['installation_date'], ascending=True)

print("valmistaja: ",module1)


# Visualisointi paneelivalmistajat
sns.countplot(module1['installation_date'])
plt.title("Uusia Paneelivalmistajia / vuosi")
plt.xlabel('vuosi')
plt.ylabel('lukumäärä')
plt.xticks(rotation=90)
plt.show()




# 
# 
# Visualisointi 'uusia Paneeli asentajia / vuosi'.
# 
# Kuvaajasta näkee miten uusia paneelien asentajia on tullut markkinoille.
# Asentajien määrä on noussut huomattavasti vasta 2015 aikana. 

# In[10]:


# paneeliasentajat: muutetaan vuosiksi ja sen mukaan sortattu
inst1['installation_date'] = pd.to_datetime(inst1['installation_date'], format='%d-%b-%Y %H:%M:%S') 
inst1['installation_date'] = inst1['installation_date'].dt.year
inst1 = inst1.sort_values(['installation_date'], ascending=True)

print("asentajat: ",inst1)


# Visualisointi paneeliasentajat
sns.countplot(inst1['installation_date'])
plt.title("Uusia Paneeliasentajat / vuosi")
plt.xlabel('vuosi')
plt.ylabel('lukumäärä')
plt.xticks(rotation=90)
plt.show()

