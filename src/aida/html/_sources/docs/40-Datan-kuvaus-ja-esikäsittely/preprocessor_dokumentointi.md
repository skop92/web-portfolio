# Esikäsittelijän dokumentaatio

Esikäsittelijä tekee lähdedatan esikäsittelyn pyrkien virheellisen datan poistoihin ja usein käytettyjen itse määriteltyjen sarakkeiden yhdenmukaiseen käsittelyyn.

## Kuvaus

### Käyttöönotto

Esikäsittelijä sijaitsee yhdessä tiedostossa, `preprocessor.py`. Esikäsittelijää on tarkoitus kutsua kyseisen tiedoston funktiolla, jonka nimi on `esik()`. Funktion käyttö on selitetty alla. Esikäsittelijä on otettava käyttöön `import` lauseella tai sitä vastaavalla tavalla. Jos esikäsittelijä sijaitsee eri kansiossa kuin kutsuva ohjelma, on kutsuvalle ohjelmalle itse kerrottava mistä esikäsittelijä löytyy.

Esimerkki `import`

```python
import importlib.util
import sys

try:
  import preprocessor as esik
except ModuleNotFoundError:
  file_path = "../Tehtava-03/preprocessor.py"; module_name = "preprocessor"; spec = importlib.util.spec_from_file_location(module_name, file_path)
  esik = importlib.util.module_from_spec(spec); sys.modules[module_name] = esik; spec.loader.exec_module(esik)
```

Lyhyemmin

```python
import importlib.util
import sys
file_path = "../Tehtava-03/preprocessor.py"; module_name = "preprocessor"; spec = importlib.util.spec_from_file_location(module_name, file_path)
esik = importlib.util.module_from_spec(spec); sys.modules[module_name] = esik; spec.loader.exec_module(esik)
```

Esimerkissä `file_path`-muuttuja ilmaisee esikäsittelijän polun. Moduulille annetaan kutsuvassa ohjelmassa nimi 'esik', eli moduulin muuttujia ja funktioita kutsuttaessa koodissa niille on annettava etuliite `esik`, jolloin esikäsittelijän kutsu on tyypillisesti muotoa `esik.esik(cols)`.

### Esikäsittelijän tapa käsitellä sarakkeita

Esikäsittelijän kutsufunktiolle on annettava ensimmäisenä parametrina lista ladattavista sarakkeista (`cols`). Listassa on oltava sarakkeiden nimet ja niiden tulee täsmätä joko lähdedatan sarakkeisiin tai itse määriteltyihin sarakkeisiin, jotka on ohjelmoitu esikäsittelijään. Aluksi esikäsittelijä käy listan läpi ja muodostaa uuden listan (`cols_extended`), johon se lisää listalla olevien sarakkeiden esikäsittelyyn vaadittavat muut sarakkeet. Seuraavaksi laajennetusta listasta muodostetaan oma lista (`extra_cols`) sen sisältämistä itse määritellyistä sarakkeista. Viimeisenä muodostetaan lista, jossa on vain lähdedatasta haettavien sarakkeiden nimet (`usecols`).

Palautuksessa käytetään vain kutsun sarakkeita (alkuperäinen `cols`).

Tällä hetkellä esikäsittelijään ei ole erikseen listattu itse määriteltyjä sarakkeita, jotka se osaa käsitellä. Täten esikäsittelijä ei anna selvää ilmoitusta siitä, jos käyttäjä yrittää ladata jonkin sarakkeen, jolle ei ole ohjelmoitu esikäsittelyä. Sen sijaan virheilmoitus indeksivirheestä on todennäköinen lopputulos.

### Itse määritellyt sarakkeet

Esikäsittelijältä voi halutessaan pyytää seuraavia sarakkeita, joita ei ole lähdedatassa.

- 'battery_storage'  
  Bool-arvo (0 tai 1), järjestelmässä on akku tai ei. Akun kuuluminen järjestelmään on päätelty siitä, jos vähintään yksi seuraavista ehdoista toteutuu:
  - akun teho on ilmoitettu ('battery_rated_capacity_kW')
  - akun kapasiteetti on ilmoitettu ('battery_rated_capacity_kWh')
  - järjestelmässä on sopiva invertteri ('solar_storage_hybrid_inverter') (tämäkään ei ole varma merkki akusta)

  Lisäksi Teslan asentamat järjestelmät voidaan lukea akullisiksi asettamalla parametrin `tesla_battery` arvoksi 'all'. Tämän on päätelty olevan mahdollista hinnoittelun perusteella.
- 'customer_segment_2'
  Alkuperäinen 'customer_segment' sarake on jaettu kahteen ryhmään:
  - RES, joka pysyy ennallaan
  - NON-RES, johon on yhdistetty muut ryhmät (COM, GOV, SCHOOL, NON-PROFIT, NON-RES)
- 'customer_segment_3'
  Jatkettuna edellisestä NON-RES on jaettu kahteen ryhmään 'system_size_DC':n perusteella. `large_limit` on oletuksena 100 kW.
  - SMALL NON-RES, 'system_size_DC' <= `large_limit`
  - LARGE NON-RES, 'system_size_DC' > `large_limit`
- 'price_per_kW'
  Laskettu yksinkertaisesti hinnan suhde tehoon. Ei lasketa, jos hintaa tai tehoa ei ole ilmoitettu tai se poistetaan esikäsittelyssä.
- 'price_per_W'
  Muutettu vain yksikkö sarakkeesta 'price_per_kW'.
- 'year'
  Asennuspäivästä erotettu asennusvuosi.

### Virheiden korjaus

Virheiden korjausta tehdään 'common' modessa. Se koskee suoraan sarakkeita

- 'system_size_DC'
  Virheiden korjauksen perusteena on laskenta, jossa järjestelmän koko lasketaan yhden paneelin tehon ja paneelinen lukumäärän tulona, joka ei saa poiketa määriteltyä virhemarginaalia (`error_margin`) enempää alkuperäisestä 'system_size_DC':n arvosta.
- 'total_installed_price'
  Hintatietoja korjataan poistamalla epärealistisia hintoja, joita etsitään 'price_per_kW' arvojen avulla. Esikäsittelijä poistaa automaattisesti myös itse asennettujen asennusten hinnat ('self_installed' != 0), jotta hintojen vertailukelpoisuus paranee. Lisäksi on mahdollista poistaa ulkopuolisten omistamien asennusten hinnat parametrilla `no_tpo_prices`, sillä kyseiset hinnat eivät välttämättä ole suoraan verrattavissa muihin hintoihin.

Ja välillisesti

- 'price_per_kW'
- 'price_per_W'

### Oletusarvot

Esikäsittelijälle on asetettu muutamia mitoittavia oletusarvoja, jotka vaikuttavat joidenkin sarakkeiden esikäsittelyyn. Nämä oletusarvot tai osa niistä on mahdollista korvata funktiokutsussa, jos niiden arvon muutoksia halutaan tutkia jatkossa. Oletusarvot on listattu kohdassa "Parametrit".

Oletusarvojen valintoja on perusteltu (vaihtelevasti) erillisissä esikäsittelyn tutkimuksissa.

## Käyttö

`esik.esik(cols, mode='common', price_per_kW_limit=1000, error_margin=0.15, large_limit=100, no_tpo_prices=False, unchecked_sizes=False, tesla_battery='neutral', sshi_with_battery=False)`

### Parametrit

  - **cols** : _list_  
  Lista sarakkeista, jotka halutaan ladata esikäsittelijällä. Voi sisältää lähdedatan sarakkeita, esikäsittelijän tuntemia itse määriteltyjä sarakkeita tai molempia. Ei oletusarvoa. Pakollinen.
  - **mode** : _str, oletus 'common'_  
  Määrää esikäsittelyn määrän.  
    - `none` estää kaiken esikäsittelyn paitsi -9999 arvojen korvaamisen NaN-arvoilla. Myös mahdolliset itse määritellyt sarakkeet jätetään lataamatta.
    - `minimal` tukee itse määriteltyjen sarakkeiden lataamista. Ei korjaa datan virheitä.
    - `common` käsittelee kaikki vaaditut sarakkeet ja korjaa virheitä datasta. On oletusarvo.
  - **price_per_kW_limit** : _int or float, oletus 1000_  
  Pienin hyväksytty hinta/teho arvo yksikössä [$/kW]. Vaikuttaa poistamalla kyseisten rivien hintatiedon. Vaikuttaa 'total_installed_price', 'price_per_kW' ja 'price_per_W' laskentaan.
  - **error_margin** : _int or float, oletus 0.15_  
  Marginaali määrittää kuinka paljon laskettu järjestelmän koko voi suhteellisesti poiketa ilmoitetusta 'system_size_DC':n arvosta, jotta esikäsittelijä hyväksyy sen alkuperäisen arvon. Ei saa olla negatiivinen.
  - **large_limit** : _int or float, oletus 100_  
  Asettaa rajan 'SMALL NON-RES' ja 'LARGE NON-RES' luokittelulle yksikössä [kW]. Raja-arvo ja sen alle jäävät luokitellaan pieniksi ja ylittävät suuriksi. Vaikuttaa vain 'customer_segment_3':n luokitteluun.
  - **no_tpo_prices** : _bool, oletus False_  
  Määrää ulkopuolisten omistamien ('third_party_owned') asennusten hintojen poiston datasta.  
    - `True` poistaa hinnat.
    - `False` ei poista hintoja. On oletusarvo.
  - **unchecked_sizes** : _bool, oletus False_  
  'system_size_DC' esikäsittelijä poistaa vain sellaiset arvot, jotka poikkeavat sallittua virhemarginaalia enemmän alkuperäisestä arvosta. Toisin sanoen arvot, joita ei voi laskemalla tarkistaa, otetaan mukaan.  
    - `True` ottaa tarkistamattomat koot mukaan.
    - `False` tarkistamattomat arvot poistetaan. On oletusarvo.
  - **tesla_battery** : _str, oletus neutral_  
  Antaa vaihtoehtoja määrittää, mitkä Tesla Energyn asennukset sisältävät akun. Vaikuttaa vain 'battery_storage' sarakkeen määritykseen.  
    - `none` määrää, että missään Tesla Energyn asennuksessa ei oleteta olevan akkua, mikä varmasti lisää virhettä.
    - `neutral` ei tee erityistä käsittelyä, joten akut tunnistetaan muiden kriteetien perusteella. On oletusarvo.
    - `all` määrää, että kaikissa Tesla Energyn asennuksissa oletetaan olevan akku.
  - **sshi_with_battery** : _bool, oletus False_  
  Tulkitaanko 'solar_storage_hybrid_inverter' merkiksi akusta. Vaikuttaa sarakkeen 'battery_storage' määritykseen.

### Paluuarvo

  - **DataFrame**  
  Kutsufunktion paluuarvo on `pandas.DataFrame`, jossa on mukana sarakkeet `cols`.