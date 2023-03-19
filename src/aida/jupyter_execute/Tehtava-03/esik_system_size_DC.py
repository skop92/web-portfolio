#!/usr/bin/env python
# coding: utf-8

# # Tutkitaan ja esikäsitellään system_size_DC
# 
# ## Pohjalle DataFrame

# In[1]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import importlib.util
import sys
file_path = "../Tehtava-03/columns_file.py"; module_name = "columns_file"; spec = importlib.util.spec_from_file_location(module_name, file_path)
cf = importlib.util.module_from_spec(spec); sys.modules[module_name] = cf; spec.loader.exec_module(cf)


cols = ['total_installed_price', 'system_size_DC', 'additional_modules', 
        'installer_name', 'self_installed', 'customer_segment', 'expansion_system']
cols.extend(cf.nameplate_capacity_module)
cols.extend(cf.module_quantity)
#cols = cf.all_orig()

url = '../data/LBNL_file.csv'
df_all = pd.read_csv(url, usecols=cols, low_memory=False, na_values = '-9999')


# ## Keskeisten sarakkeiden perustietoja
# 
# Jos 'system_size_DC':n paikkansa pitävyyttä halutaan arvioida, tarkastetaan ensin laskentaan käytettävien sarakkeisen lukuarvoja. Suodatetaan jo aluksi pois asennukset, joissa on enemmän kuin kolmea eri paneelimallia, (df['additional_modules'] == 0).

# In[2]:


df = df_all.copy()
#df = df[(df['system_size_DC'] < 1)]
df = df[(df['additional_modules'] == 0)]
#df = df[(df['additional_modules'] == 1)]
agg_func = ['size', 'count', 'min', 'max']
df.agg({
  'system_size_DC': agg_func,
  'module_quantity_1': agg_func, 'module_quantity_2': agg_func, 'module_quantity_3': agg_func,
  'nameplate_capacity_module_1': agg_func, 'nameplate_capacity_module_2': agg_func, 'nameplate_capacity_module_3': agg_func
})


# Lukemista voi päätellä, että data ei ole täysin eheää. Pienimmät asennukset ovat jopa pienempiä kuin pienimmän yksittäisen moduulin.

# ## Mitkä rivit ovat laskennallisesti kunnossa?
# 
# Pyritään löytämään rivit, jotka ovat kunnossa ja erotellaan ne omaan joukkoonsa. Etsitään rivejä aluksi seuraavilla kriteereillä:
# 
# - 'system_size_DC' on määritelty
# - vähintään yksi 'module_quantity' ja 'nameplate_capacity_module' pari on määritelty
# - jos 'module_quantity' tai 'nameplate_capacity_module' on määritelty, myös sen pari on oltava määritelty
# - 'system_size_DC' vastaa kertolaskua 'module_quantity' * 'nameplate_capacity_module' (virhemarginaali huomioitu)

# In[3]:


df = df_all.copy()
df = df[(df['additional_modules'] == 0)]
cols = ['system_size_DC']
cols.extend(cf.nameplate_capacity_module)
cols.extend(cf.module_quantity)
df[cols] = df[cols].fillna(0)

# Karsinta #1
del_1 = df[(df['system_size_DC'] == 0)]
del_2 = df[(df['module_quantity_1'] > 0) & (df['nameplate_capacity_module_1'] == 0)]
del_3 = df[(df['module_quantity_1'] == 0) & (df['nameplate_capacity_module_1'] > 0)]
df = pd.concat([df, del_1, del_2, del_3])
df['df_index'] = df.index
df.drop_duplicates(subset=['df_index'], keep=False, inplace=True)
df.drop('df_index', axis=1, inplace=True)

# Karsinta #2
del_1 = df[(df['module_quantity_2'] > 0) & (df['nameplate_capacity_module_2'] == 0)]
del_2 = df[(df['module_quantity_2'] == 0) & (df['nameplate_capacity_module_2'] > 0)]
df = pd.concat([df, del_1, del_2])
df['df_index'] = df.index
df.drop_duplicates(subset=['df_index'], keep=False, inplace=True)
df.drop('df_index', axis=1, inplace=True)

# Karsinta #3
del_1 = df[(df['module_quantity_3'] > 0) & (df['nameplate_capacity_module_3'] == 0)]
del_2 = df[(df['module_quantity_3'] == 0) & (df['nameplate_capacity_module_3'] > 0)]
df = pd.concat([df, del_1, del_2])
df['df_index'] = df.index
df.drop_duplicates(subset=['df_index'], keep=False, inplace=True)
df.drop('df_index', axis=1, inplace=True)

df[cols] = df[cols].replace(0, np.nan)
agg_func = ['size', 'count', 'min', 'max']
df_pairs = df
df_pairs.agg({
  'system_size_DC': agg_func,
  'module_quantity_1': agg_func, 'module_quantity_2': agg_func, 'module_quantity_3': agg_func,
  'nameplate_capacity_module_1': agg_func, 'nameplate_capacity_module_2': agg_func, 'nameplate_capacity_module_3': agg_func
})


# Tulokset näyttävät, että `count` lukemat täsmää, kuten suunniteltu.
# 
# ## Tarkistuslaskenta
# 
# Seuraavaksi tehdään laskutoimitukset.

# In[4]:


df = df_pairs.copy()
#df = df[(df['additional_modules'] == 0)]
cols = ['system_size_DC']
cols.extend(cf.nameplate_capacity_module)
cols.extend(cf.module_quantity)
# Muutos nolliksi, jotta laskenta onnistuu
df[cols] = df[cols].fillna(0)

# Laskenta
df['calc_size'] = ((df['module_quantity_1'] * df['nameplate_capacity_module_1']) +
                   (df['module_quantity_2'] * df['nameplate_capacity_module_2']) +
                   (df['module_quantity_3'] * df['nameplate_capacity_module_3']))

# Karsitaan nollat, koska niitä ei voi tarkistaa laskemalla muutenkaan
cols.append('calc_size')
df[cols] = df[cols].replace(0, np.nan)

# Muutos W -> kW
df['calc_size'] = df['calc_size'] / 1000
# Suhdeluku osoittaa hyvin onko vastaavuutta
df['ann_per_calc_ratio'] = df['system_size_DC'] / df['calc_size']
# Käänteinen suhdeluku
df['calc_per_ann_ratio'] = df['calc_size'] / df['system_size_DC']
# Kopio seuraavaan vaiheeseen
df_calc = df

# Tulokset
quantiles = np.arange(.05, 1, .05)
print("ann_per_calc_ratio quantiles:")
print(df['ann_per_calc_ratio'].quantile(quantiles))
df.agg({'ann_per_calc_ratio': ['count', 'min', 'max'], 'calc_size': ['count', 'min', 'max']})


# Laskenta viittaa siihen, että vähintään 80% lasketuista arvoista (n = 887974) vastaa sarakkeen 'system_size_DC' arvoa. Seuraavaksi muodostetaan näistä DataFrame huomioiden sallittu virhemarginaali.

# In[5]:


df = df_calc.copy()
# Asetetaan sallittu virhemarginaali
margin = 0.15
df_apcr_filt = df[(df['ann_per_calc_ratio'] >= (1 - margin)) & (df['ann_per_calc_ratio'] <= (1 + margin))]
df_cpar_filt = df[(df['calc_per_ann_ratio'] >= (1 - margin)) & (df['calc_per_ann_ratio'] <= (1 + margin))]
print(df_apcr_filt.agg({'ann_per_calc_ratio': ['count', 'min', 'max'], 'calc_size': ['count', 'min', 'max']}))
print(df_cpar_filt.agg({'calc_per_ann_ratio': ['count', 'min', 'max'], 'calc_size': ['count', 'min', 'max']}))


# ## Lisää tuloksia
# 
# Tehdään sama tulostus kuin alussa datalle, joka on hyväksi todettu. Huomataan ainakin, että pienimmäksi 'system_size_DC':ksi tulee 0.068 kW, joka on jo vähän uskottavampi kuin 0.0055 kW.

# In[6]:


df = df_apcr_filt.copy()
df['price_per_kW'] = df['total_installed_price'] / df['system_size_DC']
df = df[(df['price_per_kW'] > 0)]
print("Ilmoitettu / laskettu, 'price per' kW > 0, virhemarginaali:", str(100*margin), "%")
display(df.agg({
  'system_size_DC': agg_func,
  'module_quantity_1': agg_func, 'module_quantity_2': agg_func, 'module_quantity_3': agg_func,
  'nameplate_capacity_module_1': agg_func, 'nameplate_capacity_module_2': agg_func, 'nameplate_capacity_module_3': agg_func
}))
print("Laskettu / ilmoitettu, 'price per' kW > 0, virhemarginaali:", str(100*margin), "%")
df = df_cpar_filt.copy()
df['price_per_kW'] = df['total_installed_price'] / df['system_size_DC']
df = df[(df['price_per_kW'] > 0)]
display(df.agg({
  'system_size_DC': agg_func,
  'module_quantity_1': agg_func, 'module_quantity_2': agg_func, 'module_quantity_3': agg_func,
  'nameplate_capacity_module_1': agg_func, 'nameplate_capacity_module_2': agg_func, 'nameplate_capacity_module_3': agg_func
}))


# In[7]:


df = df_cpar_filt.copy()
display(df.groupby(['customer_segment']).agg({'system_size_DC': agg_func}))
#df = df[(df['system_size_DC'] == 0.068)]
#df


# ## Ongelmalliset 'system_size_DC' arvot
# 
# Käsitellään ensimmäisenä arvot, jotka karsittiin rajaamalla virhemarginaalilla. Piirretään kuvaajat suhdelukujen jakaumista.

# In[8]:


binwidth = 0.05
max_1 = 5
max_2 = 10
max_3 = 20

# Yläriviin
df = df_calc.copy()
df = pd.concat([df, df_apcr_filt])
df['df_index'] = df.index
df.drop_duplicates(subset=['df_index'], keep=False, inplace=True)
df.drop('df_index', axis=1, inplace=True)
count_1 = df['ann_per_calc_ratio'].count()

# Datan rajaus eri kuviin
df_1 = df[(df['ann_per_calc_ratio'] < max_1)]

df_2 = df[(df['ann_per_calc_ratio'] < max_2)]
df_2 = df_2[(df_2['ann_per_calc_ratio'] >= (max_1))]

df_3 = df[(df['ann_per_calc_ratio'] < max_3)]
count_2 = df_3['ann_per_calc_ratio'].count()
df_3 = df_3[(df_3['ann_per_calc_ratio'] >= (max_2))]

# Alariviin
df = df_calc.copy()
df = pd.concat([df, df_cpar_filt])
df['df_index'] = df.index
df.drop_duplicates(subset=['df_index'], keep=False, inplace=True)
df.drop('df_index', axis=1, inplace=True)
count_3 = df['calc_per_ann_ratio'].count()

# Datan rajaus eri kuviin
df_4 = df[(df['calc_per_ann_ratio'] < max_1)]

df_5 = df[(df['calc_per_ann_ratio'] < max_2)]
df_5 = df_5[(df_5['calc_per_ann_ratio'] >= (max_1))]

df_6 = df[(df['calc_per_ann_ratio'] < max_3)]
count_4 = df_6['calc_per_ann_ratio'].count()
df_6 = df_6[(df_6['calc_per_ann_ratio'] >= (max_2))]

# Piirto
size_mult = 5
fig_rows = 2
fig_cols = 3
fig, axs = plt.subplots(fig_rows, fig_cols, layout="constrained", figsize=((fig_cols*size_mult),(fig_rows*size_mult)))

sns.histplot(data=df_1, x='ann_per_calc_ratio', ax=axs[0, 0], binwidth=binwidth)
sns.histplot(data=df_2, x='ann_per_calc_ratio', ax=axs[0, 1], binwidth=binwidth)
sns.histplot(data=df_3, x='ann_per_calc_ratio', ax=axs[0, 2], binwidth=binwidth)
sns.histplot(data=df_4, x='calc_per_ann_ratio', ax=axs[1, 0], binwidth=binwidth)
sns.histplot(data=df_5, x='calc_per_ann_ratio', ax=axs[1, 1], binwidth=binwidth)
sns.histplot(data=df_6, x='calc_per_ann_ratio', ax=axs[1, 2], binwidth=binwidth)
for i in range(fig_rows):
  if i == 0:
    xlabel = 'system_size_DC per laskettu arvo'
  if i == 1:
    xlabel = 'Laskettu arvo per system_size_DC'
  for j in range(fig_cols):
    axs[i, j].set_xlabel(xlabel)
    axs[i, j].set_ylabel('Asennusten määrä')

title = f'''Laskettu 'ann_per_calc_ratio' ja 'calc_per_ann_ratio', kun virhemarginaali on {str(100*margin)} %
Ylärivi n = {str(count_2)}, kuvan ulkopuolelle jäi: n = {str(count_1 - count_2)}
Alarivi n = {str(count_4)}, kuvan ulkopuolelle jäi: n = {str(count_3 - count_4)}
'''

fig.suptitle(title)
plt.show()


# Kuvaajista on helppo päätellä, että valtaosa lasketuista arvoista on pienempi kuin datassa ilmoitettu 'system_size_DC'.

# ### Lyhyt katsaus ongelmallisiin arvoihin
# 
# Luodaan myös `df_error`, jossa on kaikki 'system_size_DC':n arvot, joita ei voitu laskennassa osoittaa luotettaviksi.

# In[9]:


df = df_all.copy()
df = pd.concat([df, df_apcr_filt])
df['df_index'] = df.index
df.drop_duplicates(subset=['df_index'], keep=False, inplace=True)
df.drop('df_index', axis=1, inplace=True)
#quantiles = np.arange(.05, 1, .05)
#print("system_size_DC quantiles:")
#print(df['system_size_DC'].quantile(quantiles))
df_error = df
df_error.agg({
  'system_size_DC': agg_func,
  'module_quantity_1': agg_func, 'module_quantity_2': agg_func, 'module_quantity_3': agg_func,
  'nameplate_capacity_module_1': agg_func, 'nameplate_capacity_module_2': agg_func, 'nameplate_capacity_module_3': agg_func
})


# In[10]:


df_error.groupby(['customer_segment']).agg({'system_size_DC': agg_func})


# ## Vertaillaan suodatusta ja korvausta
# 
# Piirretään kuvaajia koko datasta. Tutkitaan suodatuksen ja korvauksen vaikutusta hintatehosuhteeseen. Suodatettu vastaa siis laskennalla tarkistettuja arvoja ja korvaus tarkoittaa 'system_size_DC':n arvon korvaamista, jos asialliset moduulin määrä- ja tehotiedot löytyvät. Korvauksessa käytetään käytännössä vain laskennalla saatuja arvoja, joten 'system_size_DC':n arvoa ei käytetä, jos sitä ei ole voitu laskea.
# 
# Lisäksi vertailussa on mukana täysin suodattamaton data, jossa ehtona on vain se, että sekä 'total_installed_price' että 'system_size_DC' on määritelty datassa.

# In[11]:


# FormatterFunc
def no_mult(x, pos):
    """The two arguments are the value and tick position."""
    return '{:1.0f}'.format(x)

def kilo(x, pos):
    """The two arguments are the value and tick position."""
    return '{:1.1f}k'.format(x*1e-3)

binwidth = 50
max_1 = 2000
max_2 = 8000
max_3 = 16000

# Ylärivi, tiukka suodatus + virhemarginaali
df = df_apcr_filt.copy()
df['price_per_kW'] = df['total_installed_price'] / df['system_size_DC']
count_1 = df['price_per_kW'].count()

# Datan rajaus eri kuviin
df_1 = df[(df['price_per_kW'] < max_1)]

df_2 = df[(df['price_per_kW'] < max_2)]
df_2 = df_2[(df_2['price_per_kW'] >= (max_1 - binwidth))]

df_3 = df[(df['price_per_kW'] < max_3)]
plot_count_1 = df_3['price_per_kW'].count()
df_3 = df_3[(df_3['price_per_kW'] >= (max_2 - binwidth))]

# Keskirivi, 'system_size_DC' korvattu 'calc_size' 'price_per_kW' laskennassa
df = df_calc.copy()
df['price_per_kW'] = df['total_installed_price'] / df['calc_size']
count_2 = df['price_per_kW'].count()

# Datan rajaus eri kuviin
df_4 = df[(df['price_per_kW'] < max_1)]

df_5 = df[(df['price_per_kW'] < max_2)]
df_5 = df_5[(df_5['price_per_kW'] >= (max_1 - binwidth))]

df_6 = df[(df['price_per_kW'] < max_3)]
plot_count_2 = df_6['price_per_kW'].count()
df_6 = df_6[(df_6['price_per_kW'] >= (max_2 - binwidth))]

# Alarivi, suodattamaton
df = df_all.copy()
df['price_per_kW'] = df['total_installed_price'] / df['system_size_DC']
count_3 = df['price_per_kW'].count()

# Datan rajaus eri kuviin
df_7 = df[(df['price_per_kW'] < max_1)]

df_8 = df[(df['price_per_kW'] < max_2)]
df_8 = df_8[(df_8['price_per_kW'] >= (max_1 - binwidth))]

df_9 = df[(df['price_per_kW'] < max_3)]
plot_count_3 = df_9['price_per_kW'].count()
df_9 = df_9[(df_9['price_per_kW'] >= (max_2 - binwidth))]

# Piirto
size_mult = 5
fig_rows = 3
fig_cols = 3
fig, axs = plt.subplots(fig_rows, fig_cols, layout="constrained", figsize=((fig_cols*size_mult),(fig_rows*size_mult)))

sns.histplot(data=df_1, x='price_per_kW', ax=axs[0, 0], binwidth=binwidth)
sns.histplot(data=df_2, x='price_per_kW', ax=axs[0, 1], binwidth=binwidth)
sns.histplot(data=df_3, x='price_per_kW', ax=axs[0, 2], binwidth=binwidth)
sns.histplot(data=df_4, x='price_per_kW', ax=axs[1, 0], binwidth=binwidth)
sns.histplot(data=df_5, x='price_per_kW', ax=axs[1, 1], binwidth=binwidth)
sns.histplot(data=df_6, x='price_per_kW', ax=axs[1, 2], binwidth=binwidth)
sns.histplot(data=df_7, x='price_per_kW', ax=axs[2, 0], binwidth=binwidth)
sns.histplot(data=df_8, x='price_per_kW', ax=axs[2, 1], binwidth=binwidth)
sns.histplot(data=df_9, x='price_per_kW', ax=axs[2, 2], binwidth=binwidth)
for i in range(fig_rows):
  for j in range(fig_cols):
    axs[i, j].set_xlabel('Price per kW [$/kW]')
    axs[i, j].set_ylabel('Asennusten määrä')
  axs[i, 0].xaxis.set_major_formatter(no_mult)
  axs[i, 1].xaxis.set_major_formatter(no_mult)
  axs[i, 2].xaxis.set_major_formatter(kilo)

title = f'''Hintatehosuhteen arvojen jakauma

Ylärivi: suodatus (plot count / count = {str(plot_count_1)} / {str(count_1)})
Keskirivi: korvaus (plot count / count = {str(plot_count_2)} / {str(count_2)})
Alarivi: suodattamaton (plot count / count = {str(plot_count_3)} / {str(count_3)})
'''

fig.suptitle(title)
plt.show()


# Kuvaajat näyttävät pitkälti samoilta. Suurimmat erot löytyvät korvauksen käytöstä. Keskirivin kuvaajissa näkyy enemmän pieniä piikkejä oikeanpuolimmaisessa kuvassa. Lisäksi korvausta käytettäessä korkeat hintatehosuhteen arvot ovat tasaisesti suurempia. Tämä näkyy myös kuvaajan ulkopuolelle jääneiden asennusten määrässä. Tulos on yhteydessä aikaisempaan havaintoon siitä, että lasketut arvot, jotka eivät vastaa ilmoitettua arvoa, ovat enimmäkseen ilmoitettua arvoa pienempiä, jolloin hintatehosuhde nousee.
# 
# Edellä mainituista syystä johtuen korvauksen käyttö on ilmeisesti enemmän haitallista kuin hyödyllistä.
# 
# ## Loppupäätelmä
# 
# Voi olla hyvä idea lisätä esikäsittelijään mahdollisuus suodattaa data, kun halutaan karsia virheitä. Ne asennukset, joissa laskettu arvo ei ole riittävän lähellä ilmoitettua arvoa on parempi jättää ennalleen tai karsia kokonaan pois. Eli käytännössä korvaus vaikuttaa huonosti perusteltavissa olevalta vaihtoehdolta.
# 
# On hyvä muistaa yksi suodatuksen ongelma. Laskentaa ei ole tehty, jos asennuksessa on enemmän kuin kolmea eri paneelia käytössä, joka mahdollisesti turhaan karsii osan asennuksista pois. Alla katsaus näihin asennuksiin.

# In[12]:


df = df_all.copy()
df['additional_modules'] = df['additional_modules'].replace(np.nan, -1)
df = df[(df['additional_modules'] == -1)]
print("additional_modules == NaN")
display(df.groupby(['customer_segment']).agg({'system_size_DC': ['size', 'count', 'min', 'median', 'mean', 'max']}))
df = df_all.copy()
df = df[(df['additional_modules'] == 1)]
print("additional_modules == 1")
display(df.groupby(['customer_segment']).agg({'system_size_DC': ['size', 'count', 'min', 'median', 'mean', 'max']}))

