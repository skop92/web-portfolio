#!/usr/bin/env python
# coding: utf-8

# # Aurinkopaneli pisteytys koneoppimisen haasteet.
# 
# ## Aluksi
# Valitsin käytettäväksi satunnaismetsä luokittelijan ja kun en ole vielä rautainen ammattilainen niin pyrin aluksi löytämään vaan yksinkertaisen mallin josta aloittaa. Pakko kuitenkin myöntää, että data ja valittu lähestymistapa eivät olleet niin helppoja  kuin olisi voinut olettaa ja malli jääkin vielä hyvin vajavaiseksi. Muutamia kysymyksiä joita jouduin esittämään itselleni.
# * Kuka päättää mitä pisteytetään?
#     1. Koodari
#     2. Myyjä
#     2. Ostaja
#     4. Poliitikot
# * Voisiko pisteytyksen tehdä tosiaan pelkän hyötysuhteen perusteella ja hakea ominaisuuksia sen jälkeen? Esim.
#     1. Hinta
#     2. Mahdolliset lisävarusteet
#     3. Luokitus
#     4. Paras hinta kokoluokassaan jne.
# * Onko tälläisessä pisteytyksessä merkitystä siitä onko järjestelmä RES tai NON-RES jos haetaan parasta koko hinta suhdetta.
# * Millä spekseillä parasta mahdollista tuotetta haetaan?
#     * Tila parametri
#     * Tarvittava kokoluokka
#     * Tarvittavat lisävarusteet
#         * Jo nyt parhaiten hyötysuhteen mukaan pisteytetyt sisältävät lisävarusteita.
# 
# ## Datan haasteet
# Data ei ole niin suoraviivaista kuin voisi kuvitella. Hyvä esimerkki tästä on, että samaa mallia on voitu myydä erillaisella hinta/koko suhteella samana vuona. Datasta löytyy myös paljontietoja joiden totuudellisuutta on hyvä epäillä kun erot voivat olla niin räikeitä. Opetus mallista voidaan tietenkin poistaa kaikki mahdolliset outlierit ja muut arveluttavat tiedot mahdollisimman hyvin, mutta sekään ei aina kerro koko totuutta siitä miksi joku yksikkö on ollut huomattavasti kalliimpi kokoonsa nähden kuin toinen muuten saman lainen tai toisinpäin. Parhaiksi luokitellut yksiköt kuitenkin paljastivat sen, että mitä kookkaamman järjestelmän olet hankkinut sitä halvemmalla olet saanut hinta/koko suhteen. Ehkä vielä tarkempaa tutkimusta vaatisi se onko eri kokoluokkien välillä eroa valmistajien suhteen.
# 

# ## 1. Oppimistulokset
# 
# Vertasin saamiani tuloksia joissain testeissä `cut` funktiolla tehtyyn luokitteluun ja aika hyvinhänse osui kohdilleen. Tosin kyseisessä tapauksessa mietin myös, että eikö kyseinen toiminto olisi jopa tarkempi toteuttaa cut funktiolla. Tosin kun muistan, ettei mallille annettu niitä tietoja joita kyseinen funktio sai eli hyötysuhdetta niin siihen nähden se toimii kuitenkin aika näppärästi. Mietin myös muiden ominaisuuksien pisteytystä, mutta se voi tosiaan olla haastavaa ja itseasiassa jo nyt monissa parhaiksi rankatuissa oli jo muita ominaisuuksia. Mallin uudelleen kouluttamiseksi pitäisi tosin aina hakea ajantasaista dataa käsipelissä, jos ei siihen kehitetä automatiikkaa esim. että lukee automaattisesti vaikka csv tiedoston kansiosta. Mallin uudelleen koulutus vaatii kuitenkin edelleenkin samaa `cut` funktiota jolla luodaan pisteytys eli siinä mielessä ositain kyseenalaista olisiko koneoppimisesta tässä tapauksessa oikeasti hyötyä, kun sama data pystytään periaatteessa hakemaan varmasti ilman malliakin. Tätä en ehkä ajatellut kun valitsin tämän lähestymistavan. 

# ## 2-3. Erimenetelmät
# En kokeillut muita malleja kuin satunnais metsää valitettavasti ajan puutteen vuoksi, kun vertailin eri malleja arvelin sen olevan paras mahdollinen kyseiselle data setille.

# ## 4. Jatkokehitys
# Muiden ominaisuuksien hakemista tai pisteytystä ja mallin siirtoa käytäntöön on vara kehittää. Kyseisessä mallissa ei ole muutenkaan otettu huomioon kuin pelkkä 1. moduuli ja siihen liittyvä laitteisto. Jatkokehityksessä voisi ottaa huomioon jotenkin enemmän muitakin lisälaitteita.

# ## 5. Optimointi
# Optimoinnistakaan en osaa sanoa, kun nytkin toimii jo aika hyvin yli 90% todennäköisyydellä. En kokeillut optimointia tai hyperparametrejä meni niin paljon aikaa kaikenlaiseen analyysiin ja kokeiluihin. Tietysti nekin ovat myös osa optimointia.

# ## 6. Muuta huomioitavaa

# Tämä on kaikesta huolimatta ollut hyvin antoisa oppimiskokemus. 
# Vaikka ryhmältämme puuttui koneoppimiskurssi niin saimme kuitenkin aikaiseksi paljon 
