# Asennusmäärän ennustaminen

Asennusmääriä ennustetaan tässä kahdella tavalla. Ennustusmallit ovat muuten samanlaisia, mutta niissä valitaan opetusdata eri logiikalla.

Ensimmäinen malli sisällyttää opetusdataansa kaikista kuukausista alkavat aikasarjat. Toinen malli käyttää vain samasta kuukaudesta alkavia aikasarjoja kuin mistä ennusteen syöte alkaa.

**HUOM!**

Mallien tuloksiin kannattaa suhtautua varauksella, koska testeissä, jotka eivät näy dokumentaatiossa, tulokset vaihtelivat _paljon_.
