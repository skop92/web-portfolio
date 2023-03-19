#!/usr/bin/env python
# coding: utf-8

# # Aurinkopaneeleiden teknologiat

# In[1]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import importlib.util
import sys

try:
  import preprocessor as esik
except ModuleNotFoundError:
  file_path = "preprocessor.py"; module_name = "preprocessor"; spec = importlib.util.spec_from_file_location(module_name, file_path)
  esik = importlib.util.module_from_spec(spec); sys.modules[module_name] = esik; spec.loader.exec_module(esik)

try:
  import columns_file as cf
except ModuleNotFoundError:
  file_path = "columns_file.py"; module_name = "columns_file"; spec = importlib.util.spec_from_file_location(module_name, file_path)
  cf = importlib.util.module_from_spec(spec); sys.modules[module_name] = cf; spec.loader.exec_module(cf)

cols = ['installation_date', 'year', 'total_installed_price', 'system_size_DC', 'price_per_kW', 'customer_segment']
cols.extend(cf.technology_module)
cols.extend(cf.efficiency_module)
cols.extend(cf.module_quantity)
cols.extend(cf.nameplate_capacity_module)
#cols = cf.all_orig()

# esikäsittelijän ajaminen aluksi vain minimal
df_all = esik.esik(cols, 'minimal')

# FormatterFunc
def no_mult(x, pos):
    """The two arguments are the value and tick position."""
    return '{:1.0f}'.format(x)

def kilo(x, pos):
    """The two arguments are the value and tick position."""
    return '{:1.1f}k'.format(x*1e-3)

# Käytetään kaikissa kuvaajissa samoja värejä
values = df_all['technology_module_1'].value_counts().index.tolist() # uniikit arvot määrien mukaan lajiteltuna (myös NaN) listaan
values += ['muut', 'arvo puuttuu'] # lisätään vielä muut-arvo
color_palette = sns.color_palette('deep')
colors = {value: list(color_palette)[i] for i, value in enumerate(values)} # määritetään jokaiselle arvolle oma väri

# Erilaisia funktiolistoja
agg_default = ['min', 'mean', 'median', 'max']
agg_extended = ['size', 'count', 'min', 'mean', 'median', 'max']
agg_means = ['mean', 'median']
agg_counts = ['size', 'count']


# ## Paneeliteknologioiden määrät ennen esikäsittelyä

# In[2]:


df = df_all.copy()
modules = cf.technology_module
df[modules] = df[modules].fillna('arvo puuttuu') # näyeteään kuvioissa NaN-arvojen tilalla tämä teksti

def pctFormat(pct): 
    return ('%.1f' % pct)+'%' if pct > 5 else '' # formatoi kuvaajien prosenttilukuja

# Kootaan kuvaajien data
pies = dict({'data':[], 'labels':[], 'colors':[], 'titles':[]})
i=0
for module in modules:
    tm = df[module].value_counts(dropna=False)
    cut = tm.sum() * 0.02
    pies['data'].insert(i, tm.groupby(np.where(tm >= cut, tm.index, 'muut')).sum()) # ryhmitellään pienet määrät muut-kategoriaan
    pies['labels'].insert(i, [f'{key}: {pies["data"][i][key]} kpl' for key in pies['data'][i].keys()]) # luodaan labelit, joissa kpl-määrät näkyvissä
    pies['colors'].insert(i, [colors[key] for key in pies['data'][i].keys()]) # haetaan värit kuvaajaan 
    pies['titles'].insert(i, module)
    i=i+1
    if(tm.min() < cut): # jos tarvitaan muut-kuvaajaa, luodaan sille data
        pies['data'].insert(i, tm.groupby(np.where(tm < cut, tm.index, 'pois')).sum().drop('pois').sort_values(ascending=0)) # jätetään vain muut näkyviin
        pies['labels'].insert(i, [f'{key}: {pies["data"][i][key]} kpl' for key in pies['data'][i].keys()]) # luodaan labelit, joissa kpl-määrät näkyvissä
        pies['colors'].insert(i, [colors[key] for key in pies['data'][i].keys()]) # haetaan värit kuvaajaan 
        pies['titles'].insert(i, module+': muut')
        i=i+1

# Piirretään kuvaajat
fig, axes= plt.subplots(1, len(pies['data']), figsize=(20, 20))
for i, ax in enumerate(axes.flatten()):
    ax.pie(pies['data'][i], colors = pies['colors'][i], autopct = pctFormat, startangle=90, pctdistance=0.45, wedgeprops=dict(width=(.3 if ((i +1) % 2) == 1 else 1)))
    ax.set_title(pies['titles'][i],)
    ax.legend(loc=3, prop={'size': 9}, labels=pies['labels'][i])
    fig = ax.get_figure()
    fig.tight_layout()
    fig.subplots_adjust(top=1.68)
plt.suptitle('Paneeliteknologioiden määrät ennen esikäsittelyä', x=0, horizontalalignment='left', fontweight ='bold', fontsize=20)
plt.show()


# ## Paneeliteknologioiden määrät esikäsittelyn jälkeen
# 
# * Poly ja multi-c-Si tarkoitetaan samaa Polychrystalline -teknologiaa -> yhdistetään Poly:ksi
# * a-Si, CIGS js CdTe ovat Thin Film -paneelien alaluokkia ja näitä on hyvin pieniä määriä -> yhdistetään nämä Thin Film alle
# * muutetaan < undefined > -arvot NaN-arvoiksi

# In[3]:


df = df_all.copy()
# Tietoa paneeliteknologioista: https://aurorasolar.com/blog/solar-panel-types-guide/

# esikäsittelyjä, jotka lisätty myös esikäsittelijään (prepsocessor.py)
df[modules] = df[cf.technology_module].replace('Multi-c-Si', 'Poly') # Poly ja multi-c-Si sama asia
df[modules] = df[cf.technology_module].replace(['a-Si', 'CIGS', 'CdTe'], 'Thin Film') # Thin Film -paneelien alaluokkia, yhdistetään
df[modules] = df[cf.technology_module].replace('<undefined>', np.nan) # <undefined> -arvo pois

df_all = df # päivitetään muutokset myös alussa ladattuun dataan
colors = {value: list(color_palette)[i] for i, value in enumerate(df_all['technology_module_1'].value_counts().index.tolist())} # päivitetään värit

modules = cf.technology_module[:-1] # kolmatta tyhjää saraketta ei tarvita

def pctFormat(pct): 
    return ('%.1f' % pct)+'%' if pct > 0 else '' # formatoi kuvaajien prosenttilukuja

# Kootaan kuvaajien data
pies = dict({'data':[], 'labels':[], 'colors':[], 'titles':[]})
i=0
for module in modules:
    tm = df[module].value_counts(dropna=False)
    cut = tm.sum() * 0
    pies['data'].insert(i, tm.groupby(np.where(tm >= cut, tm.index, 'muut')).sum()) # ryhmitellään pienet määrät muut-kategoriaan
    pies['labels'].insert(i, [f'{key}: {pies["data"][i][key]} kpl' for key in pies['data'][i].keys()]) # luodaan labelit, joissa kpl-määrät näkyvissä
    pies['colors'].insert(i, [colors[key] for key in pies['data'][i].keys()]) # haetaan värit kuvaajaan 
    pies['titles'].insert(i, module)
    i=i+1
    if(tm.min() < cut): # jos tarvitaan muut-kuvaajaa, luodaan sille data
        pies['data'].insert(i, tm.groupby(np.where(tm < cut, tm.index, 'pois')).sum().drop('pois').sort_values(ascending=0)) # jätetään vain muut näkyviin
        pies['labels'].insert(i, [f'{key}: {pies["data"][i][key]} kpl' for key in pies['data'][i].keys()]) # luodaan labelit, joissa kpl-määrät näkyvissä
        pies['colors'].insert(i, [colors[key] for key in pies['data'][i].keys()]) # haetaan värit kuvaajaan 
        pies['titles'].insert(i, module+': muut')
        i=i+1

# Kootaan data myös Yhteensä-kuvaan
tm = df['technology_module_1'].value_counts(dropna=True) + df['technology_module_2'].value_counts(dropna=True)
pies['data'].append(tm.groupby(np.where(tm >= cut, tm.index, 'muut')).sum()) # ryhmitellään pienet määrät muut-kategoriaan
pies['labels'].append([f'{key}: {pies["data"][i][key]} kpl' for key in pies['data'][i].keys()]) # luodaan labelit, joissa kpl-määrät näkyvissä
pies['colors'].append([colors[key] for key in pies['data'][i].keys()]) # haetaan värit kuvaajaan 
pies['titles'].append('Yhteensä')

# Piirretään kuvaajat
fig, axes= plt.subplots(1, len(pies['data']), figsize=(10, 10))
for i, ax in enumerate(axes.flatten()):
    ax.pie(pies['data'][i], colors = pies['colors'][i], autopct = pctFormat, startangle=90, pctdistance=0.45, wedgeprops=dict(width=.3))
    ax.set_title(pies['titles'][i],)
    ax.legend(loc=3, prop={'size': 9}, labels=pies['labels'][i])
    fig = ax.get_figure()
    fig.tight_layout()
    fig.subplots_adjust(top=1.50)
plt.suptitle('Paneeliteknologioiden määrät esikäsittelyn jälkeen', y=1, x=0, horizontalalignment='left', fontweight ='bold', fontsize=20)
plt.show()


# ## Vuosittaista dataa teknologia-sarakkeista

# In[4]:


tm1 = df_all.groupby(['year', 'technology_module_1']).agg({'efficiency_module_1': agg_extended, 'system_size_DC': agg_means, 'price_per_kW': agg_means, 'module_quantity_1': agg_means, 'nameplate_capacity_module_1': agg_means}).round(2)
tm1


# In[5]:


tm2 = df_all.groupby(['year', 'technology_module_2']).agg({'efficiency_module_2': agg_extended, 'system_size_DC': agg_means, 'price_per_kW': agg_means, 'module_quantity_2': agg_means, 'nameplate_capacity_module_2': agg_means}).round(2)
tm2


# ## Datan käsittelyä ennen kuvaajien piirtämistä

# In[6]:


display(df.agg({
  'price_per_kW': agg_extended,
  'technology_module_1': agg_counts, 'technology_module_2': agg_counts,
  'efficiency_module_1': agg_extended, 'efficiency_module_2': agg_extended
}))

# koska mukaan kuvaajiin tulee myös hintatehosuhde, ajetaan esikäsittelijä tässä välissä uudelleen common-moodissa
df = esik.esik(cols, 'common')

display(df.agg({
  'price_per_kW': agg_extended,
  'technology_module_1': agg_counts, 'technology_module_2': agg_counts,
  'efficiency_module_1': agg_extended, 'efficiency_module_2': agg_extended
}))

# Luodaan dataframe, jossa 1,2,3 sarakeryhmistä kustakin moduulikohtaiset rivit dataframessa
from re import sub
excp = '(?<!data_provider)(?<!system_ID)' # sarakkeet, joissa myös numeerinen pääte, mutta joihin ei haluta koskea
# Pudotetaan sarakeryhmät 2 ja 3 pois ja nimetään 1 sarakkeet uudelleen poistamalla _1 sarakkeiden lopusta
df_1 = df[df.columns.drop(list(df.filter(regex=excp+'(_2|_3)')))].rename(columns=lambda s: sub(excp+'_1', '', s))
df_1.insert(0, 'module_grp', 1) # säilytetään tieto mikä sarakeryhmä kyseessä
df_1.insert(0, 'inst_id', df_1.index) # ja asennus id kyseessä
df_2 = df[df.columns.drop(list(df.filter(regex=excp+'(_1|_3)')))].rename(columns=lambda s: sub(excp+'_2', '', s))
df_2.insert(0, 'module_grp', 2)
df_2.insert(0, 'inst_id', df_2.index)
df_3 = df[df.columns.drop(list(df.filter(regex=excp+'(_2|_1)')))].rename(columns=lambda s: sub(excp+'_3', '', s))
df_3.insert(0, 'module_grp', 3)
df_3.insert(0, 'inst_id', df_3.index)
df_123 = pd.concat([df_1, df_2, df_3]).reset_index() # yhdistetään dataframet
df_123['technology_module'] = df_123['technology_module'].dropna() # pudotetaan pois NaN-rivejä

# tarkistuksia
display(df_123.head(0))
display(df[cf.technology_module].agg(agg_counts))
display(df[cf.technology_module].count().sum())
display(df_123[['technology_module']].agg(agg_counts))


# ## Paneeliteknologioiden asennusmäärät vuosittain
# 
# * Mono-teknologian paneeleiden asennusmäärät vuodesta 2014 lähtien jyrkässä nousussa.
# * Poly-teknologian paneeleilla mielenkiintoinen jyrkkä nousu 2012-15 ja jyrkkä lasku 2016-19.
# * Thin Film -paneeleiden asennusmäärät datassa minimaalisia.

# In[12]:


df = df_123.copy()

df = df[df['installation_date'] > '2001-01-01']
xticks = df['year'].unique()
df = df.groupby(['year'])['technology_module'].value_counts(normalize=False).unstack().dropna()

df.plot(grid=True, linewidth=3, figsize=(15,5), xlabel="Vuosi", ylabel="Asennusmäärä")
plt.title("Paneeliteknologioiden asennusmäärät vuosittain")
plt.xticks(xticks, labels=xticks)
plt.legend(labels=('Mono', 'Poly', 'Thin Film'), title='Paneeliteknologia')
sns.set_style("darkgrid")
plt.show()


# ## Paneeliteknologioiden hyötysuhteen kehitys
# 
# * Mono-teknologialla koko datan aikajaksolla 2013-2019 paras hyötysuhde.
# * Poly-teknologian hyötysuhde nousee tasaisesti 13% -> 18%.
# * Mono ja Thin Film -paneelien osalta hyötysuhde pääasiassa nousee, mutta vuosien 2009-2011 välillä myös laskee. Mikä voisi selittää tämän notkahduksen?
# * Thin Film -paneelien hyötysuhteessa merkittävän jyrkkä kasvu lyhyessä ajassa vuosien 2012-2014 välillä.

# In[8]:


df = df_123.copy()

df = df[df['installation_date'] > '2002-01-01']
xticks = df['year'].unique()

df = df.groupby(['year', 'technology_module']).agg({'efficiency_module': 'mean'}).unstack().dropna()

df.plot(grid=True, linewidth=3, figsize=(15,5), xlabel="Vuosi", ylabel="Hyötysuhde (%)")
plt.title("Paneeliteknologioiden hyötysuhteen kehitys")
plt.xticks(xticks, labels=xticks)
plt.legend(labels=('Mono', 'Poly', 'Thin Film'), title='Paneeliteknologia')
sns.set_style("darkgrid")
plt.show()


# ## Paneeliteknologioiden hintatehosuhteen kehitys
# 
# * Asennuksista löytyy vain kokonaishinta, josta ei ole mahdollista eritellä mahdollisten eri teknologiaa olevien moduuleiden osuuksia erikseen.
# * Kuvaajassa näytetään vain asennukset, joissa käytetty yhtä paneeliteknologiaa.
# * Lisäksi käytetty esikäsittelijä-kirjastoa common-moodissa, jolla tehdään aiemmin sarakkeisiin määriteltyjä esikäsittelyjä automaattisesti.

# In[9]:


df = df_all.copy()

# pudotetaan pois asennukset, joissa käytetty samassa useampia eri teknologioita
df = df[(df['technology_module_2'].isna()) & (df['technology_module_3'].isna())]

df = df[df['installation_date'] > '2004-01-01']
xticks = df['year'].unique()

df = df.groupby(['year', 'technology_module_1']).agg({'price_per_kW': 'mean'}).unstack().dropna()

df.plot(grid=True, linewidth=3, figsize=(15,5), xlabel="Vuosi", ylabel="Hintatehosuhde ($/kW)")
plt.title("Paneeliteknologioiden hintatehosuhteen ($/kW) kehitys")
plt.xticks(xticks, labels=xticks)
plt.legend(labels=('Mono', 'Poly', 'Thin Film'), title='Paneeliteknologia')
sns.set_style("darkgrid")
plt.show()


# ## Paneeliteknologioiden keskimääräinen nimellisteho (W)
# 
# * Mono-teknologian paneelien keskimääräinen nimellisteho kaksinkertaisutunut 2007-2019 välillä ~150W -> 300W.
# * Myös Poly-teknologian paneeleilla nimellisteho noussut tasaisesti.
# * Thin Film-paneelien keskimääräinen nimellisteho 2003-2013 pieni ~100W, jonka jälkeen arvo 2.5 kertaistuu 2013-2019 välillä.

# In[10]:


df = df_123.copy()

df = df[df['installation_date'] > '2002-01-01']
xticks = df['year'].unique()

df = df.groupby(['year', 'technology_module']).agg({'nameplate_capacity_module': 'mean'}).unstack().dropna()

df.plot(grid=True, linewidth=3, figsize=(15,5), xlabel="Vuosi", ylabel="Nimellisteho (W)")
plt.title("Paneeliteknologioiden keskimääräinen nimellisteho (W)")
plt.xticks(xticks, labels=xticks)
plt.legend(labels=('Mono', 'Poly', 'Thin Film'), title='Paneeliteknologia')
sns.set_style("darkgrid")
plt.show()


# ## Paneeliteknologioiden keskimääräinen paneelien määrä asennuksessa
# 
# * Mono- ja Poly-paneelien keskimääräiset asennuskohtaiset määrät eivät juuri aikajaksolla muutu.
# * Thin Film-paneelien keskimääräiset asennuskohtaiset määrät heittelevät laajalla skaalalla ja ovat paikoin huomattavan isoja.

# In[11]:


df = df_123.copy()

df = df[df['installation_date'] > '2002-01-01']
xticks = df['year'].unique()

df = df.groupby(['year', 'technology_module']).agg({'module_quantity': 'mean'}).unstack().dropna()

df.plot(grid=True, linewidth=3, figsize=(15,5), xlabel="Vuosi", ylabel="Paneelien määrä asennuksessa")
plt.title("Paneeliteknologioiden keskimääräinen paneelien määrä asennuksessa")
plt.xticks(xticks, labels=xticks)
plt.legend(labels=('Mono', 'Poly', 'Thin Film'), title='Paneeliteknologia')
sns.set_style("darkgrid")
plt.show()

