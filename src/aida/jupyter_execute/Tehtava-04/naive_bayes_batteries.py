#!/usr/bin/env python
# coding: utf-8

# # Naive Bayes -luokittelua akkujärjestelmille
# 
# Tässä luodaan esikäsittelijän ja lisäesikäsittelyn avulla otos datasta, jolla testataan kahden Naive Bayes -luokittelijan kykyä päätellä, onko järjestelmässä akku pelkän hinnan [$/W] ja asentajan perusteella.
# 
# ## Kirjastot

# In[1]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.naive_bayes import GaussianNB
from sklearn.naive_bayes import ComplementNB
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import importlib.util
import sys
file_path = "../Tehtava-03/preprocessor.py"; module_name = "preprocessor"; spec = importlib.util.spec_from_file_location(module_name, file_path)
esik = importlib.util.module_from_spec(spec); sys.modules[module_name] = esik; spec.loader.exec_module(esik)


# ## Esikäsittelijän ajaminen
# 
# Kutsutaan esikäsittelijää. Käytetään oletusasetuksia eli annetaan parametrina vain lista tarvittavista sarakkeista.

# In[2]:


price_col = 'price_per_W'
customer_segment = 'customer_segment'
cols = ['year', price_col, 'installer_name', 'battery_storage', customer_segment]

df_all = esik.esik(cols)

print("df_all.shape:", df_all.shape)


# ## Datan käsittely malleja varten
# 
# Luokittelun perustana on hinta ja asentaja, joten poistetaan rivit, joilta kyseiset tiedot puuttuvat. Supistetaan testidataa lisää ensimmäisiä testejä varten rajaamalla se yhteen vuoteen ja yhteen asiakassegmenttiin. Joukosta poistetaan myös kalleimmat järjestelmät ja valitaan vain tietty määrä supistetun joukon yleisimpiä asentajia, joista tehdään omat sarakkeet `pd.get_dummies` metodilla. Lopuksi poistetaan sarakkeet, joita ei käytetä mallin ajossa.

# In[3]:


top_installers_n = 25
price_limit_quantile = 0.95

df = df_all.copy()
df.dropna(subset=[price_col, 'installer_name'], inplace=True)
print("dropna, df.shape:", df.shape)

df = df[(df['year'] == 2018)]  # Ensimmäinen akku 2008
print("1-year, df.shape:", df.shape)

df = df[(df[customer_segment] == 'RES')]
print("1-segment, df.shape:", df.shape)

price_q = df[price_col].quantile(price_limit_quantile)
print(price_limit_quantile, "quantile:", price_q)
df = df[(df[price_col] <= price_q)]
print("price limit, df.shape:", df.shape)

installers = df['installer_name'].value_counts().head(top_installers_n).index.tolist()
df = df[(df['installer_name'].isin(installers))]
print(top_installers_n, "top installers, df.shape:", df.shape)

display(df['battery_storage'].value_counts())
display(df.groupby(['installer_name']).agg({'battery_storage': ['count', 'mean']}).sort_values(by=('battery_storage', 'mean'), ascending=False).head())
df.rename(columns={'installer_name': 'i'}, inplace=True)
df = pd.get_dummies(df, columns=['i'])

df.drop(['year', customer_segment], axis=1, inplace=True)
print("df.shape:", df.shape)
display(df.head(2))
df_ML = df


# ## Mallien ajo
# 
# Käytetään edellisessä lohkossa valikoitua dataa mallien koulutukseen. Aloitetaan jakamalla data opetus- ja testidataa. Tämän jälkeen tehdään hinnan skaalaus välille [0, 1]. Säilytetään kuitenkin alkuperäiset arvot taulukoissa `X_train_orig` ja `X_test_orig`, sillä niitä käytetään myöhemmin tulosten tarkastelussa.

# In[4]:


df = df_ML.copy()
X = df.drop('battery_storage', axis=1)
y = df['battery_storage']
X_cols = X.columns

X_train_orig, X_test_orig, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=5451, stratify=y)

mms = MinMaxScaler().fit(X_train_orig)

X_train = pd.DataFrame(mms.transform(X_train_orig), columns=X_cols)
X_test = pd.DataFrame(mms.transform(X_test_orig), columns=X_cols)

X_train.head()


# ## Luokittelu ja sen tarkkuus
# 
# ### GaussianNB

# In[5]:


gnb = GaussianNB()

y_pred_G = gnb.fit(X_train, y_train).predict(X_test)
acs = accuracy_score(y_test, y_pred_G)
cm = confusion_matrix(y_test, y_pred_G)
print(f'Accuracy: {acs}')
print(f'{cm}')


# ### ComplementNB

# In[6]:


clf = ComplementNB()

y_pred_C = clf.fit(X_train, y_train).predict(X_test)
acs = accuracy_score(y_test, y_pred_C)
cm = confusion_matrix(y_test, y_pred_C)
print(f'Accuracy: {acs}')
print(f'{cm}')


# ## Mitä luokittelu käytännössä teki?
# 
# Analyysin syventämiseksi piirretään kuvaajat molemmille malleille sekä alkuperäiselle testisetin datalle. Ilman akkua olevien järjestelmien hintajakauma on kuvassa ylärivillä ja akkujärjestelmien alarivillä.
# 
# Tulokset kootaan ensin yhteen taulukkoon (DataFrame).

# In[7]:


model = 'model'
ind = X_test_orig.index

df_1 = pd.concat([X_test_orig, y_test], axis=1)
df_1[model] = 'original'

df_2 = pd.concat([X_test_orig, pd.Series(y_pred_G, index=ind, name='battery_storage')], axis=1)
df_2[model] = 'gaussian'

df_3 = pd.concat([X_test_orig, pd.Series(y_pred_C, index=ind, name='battery_storage')], axis=1)
df_3[model] = 'complement'

df = pd.concat([df_1, df_2, df_3])

sns.displot(
  df, x=price_col, col=model, row='battery_storage',
  binwidth=.2, height=3, facet_kws=dict(margin_titles=True)
)
plt.show()


# Saattoi olla odotettuakin, että Bayes-luokittelijat luokittelevat 5,0-5,2 kohdalla olevan piikin pääsääntöisesti akullisiksi, sillä kyseessä on suurimmaksi osaksi Tesla Energyn samanhintaiset asennukset, joista vain osassa on tietoja akusta. Malli on siis ainakin jossain määrin toiminut niin kuin odotettiin, kun se tulkitsi hinnan ja asentajan perusteella lähes kaikki samassa ryppäässä olleet asennukset akullisiksi.
# 
# Mallien tarkkuus jää toki epätarkaksi. Se on toisaalta hyvä merkki, sillä oletus oli, että potentiaalisia akkujärjestelmiä on löydettävissä enemmän kuin mitä datan varmemmat merkit antavat ymmärtää. Mallin varsinaista tarkkuutta ei taas toisaalta voida laskea, koska tarkastusdataa ei oletettujen puutteiden vuoksi ole. Toisin sanoen mallien hyvyyden arviointi on tehtävä vain tuloksen järkevyyden ja realistisuuden perusteella.

# ### Akkujärjestelmien osuus
# 
# Lasketaan vielä akkujärjestelmien osuus kaikista asennuksista kullekin mallille.

# In[8]:


display(df.groupby([model]).agg({'battery_storage': ['mean']}))
display(df.groupby([model, 'battery_storage']).agg({price_col: ['count', 'mean']}))


# Alkuperäisessä datassa osuus on noin 5 %. Tämä täsmää hyvin dataa analysoineen _Lawrence Berkeley National Laboratory_:n laskelmiin, mikä herättää epäilyksiä aikaisemmin tehdyn oletuksen pätevyydestä. Oletus, että akkujärjestelmiä olisi enemmän kuin akuista on tietoa, saattaa sittenkin olla väärä. Ehkä sama hinnan ja tehon suhde järjestelmille akulla ja ilman esimerkiksi Tesla Energyn kohdalla johtuu jostain muusta syystä, kuten virheistä hintatiedoissa. Esikäsittelyvaiheessa tuskin onnistuttiin korjaamaan kaikkia epäselvyyksiä hinnoista.
# 
# #### Mallin tuloksia asentajien mukaan
# 
# Tarkastellaan myös asentajakohtaisesti miten mallit ovat luokitelleet akkuja.

# In[9]:


i_cols = df.columns.tolist()
# Kaikki mukana olleet asentajat
installers = []
for i in range(len(i_cols)):
  if (i_cols[i].startswith('i_')):
    installers.append(i_cols[i])

# Valitaan vain osa näytille
installers = ['i_Complete Solar', 'i_Freedom Forever', 'i_Nb Baker Electric', 'i_Rec Solarmmercialrp']

# Tulostus
for installer in installers:
  df_1 = df[(df[installer] == 1)]
  print(installer)
  display(df_1.groupby([model, 'battery_storage']).agg({price_col: ['count', 'mean', 'min', 'max']}))


# Kun valittiin 25 eniten asennuksia tehnyttä asentajaa, näiden joukossa oli paljon niitä asentajia, jotka eivät ole asentaneet akkuja. Näiden kohdalla mallit eivät ole luokitelleet yhtään järjestelmää akulliseksi.
# 
# Akkuja asentaneiden kohdalla tilanne on toinen. Mallit joko olettavat asentajan kaikki asennukset akullisiksi tai akuttomiksi. Hinnan merkitys siis katoaa.
# 
# Jos mallinnukseen valittavien asentajien määrää lasketaan alle viiteen, hinnan vaikutus alkaa näkyä.
# 
# ## Loppupäätelmät
# 
# Tulos sekä antoi vastauksia että jätti kysymyksiä. Ehkäpä jokin muu malli olisi antanut parempia tuloksia, mutta näissäkin tuloksissa riittäisi vielä tutkittavaa.
# 
# Viimeisimpänä tutkittu luokittelun tulos asentajittain osoitti, että luokittelijoiden päätökset perustuvat käytännössä lähes täysin asentajaan. Hintakin vaikuttaa, mutta vain pieni joukko halvimpia asennuksia luokitellaan akuttomaksi.
# 
# Ajamalla koko mallin eri `top_installers_n` arvoilla voi huomata, että pienillä arvoilla hinnalla on enemmän vaikutusta. Kun muuttujan arvo on noin 10 tai suurempi, hinnan merkitys näyttää katoavan kokonaan.
# 
# Akun vaikutusta hintaan voisi tutkia myös lineaarisella regressiomallilla.
# 
# ### Havainto datasta
# 
# Tätä luokittelua tehdessä käsitys datasta muuttui akkujen osalta huomattavasti. Epäily siitä, että akkukomponenttien tietoja puuttuisi datasta huomattavan paljon vaihtui voimistuneeseen epäilyyn siitä, että osaa datan hintatiedoista on joko vääristelty tai niissä huomioidaan vain osa asennuksen kustannuksista vaihtelevin tavoin.
# 
# Ristiriitaisuus johtuu pääosin oletuksesta, että asennuksen hinnan [$/W] pitäisi olla selvästi korkeampi akulla kuin ilman akkua, mutta samalla asentajallakin on datassa samanhintaisia asennuksia akulla ja ilman (esimerkiksi Tesla Energy). Joko oletus on väärin, hinnat ovat osin väärin tai _Lawrence Berkeley National Laboratory_ on laskenut akut väärin. Todennäköisimmin suurin ongelma näistä on hintojen täsmällisyys ja vertailukelpoisuus.
