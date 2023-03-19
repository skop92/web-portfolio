# Klusteroinnin analysointia

Linkki edellisen tehtävän notebookiin: [maantieteellista_klusterointia.ipynb](https://student.labranet.jamk.fi/~AB5154/aida_build/maantieteellista_klusterointia.html)

## Lähtötavoite

Projektissa toteutetun klusteroinnin tavoitteena on ollut muodostaa asennusten postinumeroille erillisestä csv-tiedostosta haettujen koordinaattien perusteella maantieteellisiä "kuumia pisteitä", joissa aurinkopaneeleita on asennettu eniten.

Klusteroitua dataa on pyritty tämän jälkeen visualisoimaan erilaisilla karttakuvaajilla. Näihin on mahdollista sisällyttää erilaista hyödyllistä tietoa asennuksista, kuten esimerkiksi asennusten keskimääräinen hinta tai asennettujen järjestelmien keskimääräinen teho.

Projektin datan kohdalla on kuitenkin mietittävä, tuoko klusterointi mitään käytännön lisäarvoa verrattuna siihen, että näytettäisiin kartalla suoraan isoimmat kaupungit tai postinumeroalueet asennusten määrittäin.

Klusterointi sopiikin paremmin tapauksiin, jossa sijaintidata on satunnaisempaa, eikä pohjaluokittelua (kaupungit/postinumerot) ole olemassa. Eli silloin, kun datasta ei ole mahdollista ilman klusterointia saada selkeää maantieteellistä kuvaa.

## Valittu menetelmä

Lähtökohtana menetelmän valitsemiselle oli, että kaikkia pisteitä ei haluta sisällyttää mukaan klustereihin ja, että klustereiden määrää ei tarvitse etukäteen määrittää. Myös menetelmän ajamiseen vaadittava aika oli merkittävä kriteeri valinnassa.

Klusteroinnin menetelmäksi valittu DBSCAN- soveltuukin erittäin hyvin isoihin datamääriin. Menetelmä on nopea käyttää pääasiassa, koska eps-parametri eli säde, jolta alueelta kullekin datapisteelle etsitään muita saman klusterin pisteteitä, rajoittaa eri haettavien vaihtoehtojen määrää runsaasti.

Tämä tekee samalla myös parametrien asettamisesta haastavaa ja vaatii datan tuntemusta. Liian pienellä eps-arvolla klustereista tulee pieniä ja liian suurella muodostuu maantieteellisesti turhan isoja klustereita.

Toinen DBSCAN:in tärkeä määritettävä parametri on min_samples, jonka perusteella menetelmä arvioi onko klusterin alueella riittävästi pisteitä klusterin muodostamiseen. Datassa on paljon samoja pisteitä, joita normaalisti koneoppimisessa haluttaisiin karsia. Tässä tapauksessa nämä ovat kuitenkin olennaista tietoa, koska tavoitteena on nimenomaan löytää määrällisesti merkittävät sijainnit.

Parametrien haastavan määrittämisen lisäksi DBSCAN:nin miinuspuolena on, ettei tämä palauta klustereille keskipisteitä automaattisesti. Vaikka näiden laskeminen onkin melko yksinkertaista toteuttaa esimerkiksi Shapely-kirjastosta löytyvällä valmiilla funktiolla, hidastaa tämä huomattavasti koodin ajamista.

## Vaihtoehtoiset menetelmät

Ensimmäisenä klusteroinnin menetelmänä kokeilin ehkä kaikkein yleisimmin käytettyä K-Means-klusterointia. Tämä karsiutui kuitenkin jo hetialkumetreillä pois, koska menetelmässä klustereiden määrä on määritettävä etukäteen eikä mitään pisteitä suodateta pois.

Lähimpänä DBSCAN:ia vastaavia klusteroinnin menetelmiä löysin kaksi: OPTICS ja HDBSCAN, jotka kummatkin on kehitetty alun perin DBSCAN:in pohjalta ja mukana on ollut samoja kehittäjiä. Kumpikin näistä saattaisi pienemmillä datamäärillä soveltua DBSCAN:ia hieman paremmin tuotantokäyttöön.

Etukäteen vaadittavia pakollisia ja tarkasti määritettäviä parametreja, kuten eps (säde), ei juurikaan ole, joten automatisointikin olisi todennäköisesti yksinkertaisempaa.

Merkittävä miinuspuoli näissä on kuitenkin mallin ajamiseen kuluva aika, koska laskettavien vaihtoehtojen määrä on ilman rajoituksia myös huomattavasti suurempi. Aikaa kului isolla datamäärällä usein monin kymmenkertaisesta siihen, että Jupyter kaatui muistin loppuessa kesken.

Myöskään varsinaiset tulokset näiden joidenkin kymmenien ajokokeilujen perusteella eivät visuaalisella tarkastelulla niin paljon poikenneet DBSCAN:ista, että tämän projektin puitteissa nämä olisivat olleet parempia vaihtoehtoja.

## Tuotantoon soveltaminen

Jotta DBSCAN:ista pystyisi järkevästi soveltamaan tuotantoon, vaatisi tämä todennäköisesti optimaalisten parametrien löytämiseksi jotain automatisointia. Yritin projektin aikana miettiä olisiko parametrien löytämiseksi mahdollista toteuttaa tähän tarkoitukseen jonkinlainen algoritmi.

Eps-parametri riippuu postinumeroiden etäisyyksistä, joten periaatteessa laskemalla datan pisteille keskiarvoinen etäisyys ja soveltamalla tämän arvon pohjalta jonkinlainen algoritmi, tämä voisi olla mahdollista. Käytännössä näin isossa datamäärässä tämä olisi melko raskas operaatio ajaa jokaiselle datapisteelle erikseen, vaikka duplikaatit voisikin tässä laskennassa poistaa ensin turhina.

Min_samples-parametrin osalta koitin laskea datasta asennusten määristä eri kvartaalin arvoja ja säätää tätä hieman erilaisilla kertoimilla. Käytännössä tämä ei kuitenkaan oikein onnistunut.

## Jatkokehitys ja muita huomioita

Myös projektin datan ulkopuolisista lähteistä olisi mahdollista eri rajapintojen avulla liittää postinumeroihin, kaupunkien nimiin tai koordinaatteihin tietoa väestöpohjasta tai esimerkiksi alueen varallisuudesta. Tämä mahdollistaisi useita väyliä laajentaa projektia ja voisi olla hyödyllistä jonkinlaista liiketoimintaakin ajatellen.

Projektin aikana pohdinnoissa nousi esille myös koneoppimisvaiheessa yhtenä toisena mallina toteutetun asennusten määrien ennustuksen liittäminen klusteroinnin visualisoinnin jatkoksi vuosittaiseen asennusten määrien animaatioon.

Toinen ajatuksena kiinnostava esiin noussut vaihtoehto oli eräänlaisen markkinasaturaation perustuva liiketoimintamahdollisuuksien "metsästäminen" eli pyrkiä koneoppimisen menetelmin ennustamaan potentiaalisia sijainteja, joissa tulevaisuudessa asennuksille olisi eniten kysyntää ja nouseva trendi.

Nämä jäivät kuitenkin tämän projektin puitteissa ideatasolle ja oli tärkeämpää keskittyä koneoppimisessa olennaisempaan.
