# magyar


## Magyar listák gyűjteménye - Collection of Hungarian lists.

Az alábbi listákat találod :
1. Magyar vezetéknevek   =  magyar.**vezeteknev**
2. Magyar női keresztnevek  = magyar.**keresztnev_n**
3. Magyar férfi keresztnevek = magyar.**keresztnev_f**
4. Magyar vegyes keresztnevek= magyar.**keresztnev_v**
5. Magyar utcanevek = magyar.**utca**
6. Magyar telelpülésnevek= magyar.**telepules**
7. Magyar vármegyék nevei = magyar.**megye**
8. Magyar folyók nevei = magyar.**folyo**
9. A hét napjai magyarul = magyar.**nap**
10. Az év hónapjai magyarul = magyar.**honap**
11. A gyümölcsök magyar nevei = magyar.**gyumolcs**
12. A zöldségek magyar nevei = magyar.**zoldseg**
13. A haszonállatok magyar nevei = magyar.**haszonallat**
14. Vadallatok Magyarországon = magyar.**vad**
15. Magyarország halai = magyar.**hal**
16. Magyarország madarai = magyar.**madar**
17. A naprendszer bolygóinak magyar neve = magyar.**bolygo**
18. Magyar leves nevek =  magyar.**leves**
19. Magyar főételek = magyar.**foetel**
20. Magyar köretek = magyar.**koret**
21. Magyar egytál ételek = magyar.**egytal**
22. Magyar desszertek = magyar.**desszert**
23. Magyar borok = magyar.**bor**
24. Magyar üdítők= magyar.**udito**

## Szótárak  (dictionary): 
1. Királyok és uralkodásuk ideje  = magyar.kiraly
2. Vármegyék és azok székhelyei = magyar.megye_szekhely
3. Járások, székhelyük , megye = magyar.jaras
4. Villamosvonalak, végállomások, menetidő = magyar.villamos
5. Európa országai és fővárosai=  magyar.orszag

## Description
1. Last names =  magyar.**vezeteknev**
2. Female first names = magyar.**keresztnev_n**
3. Male first names  = magyar.**keresztnev_f**
4. Street names = magyar.**utca**
5. City names = magyar.**telepules**
6. Names of counties = magyar.**megye**
7. Names of rivers = magyar.**folyo**
8. The days of the week = magyar.**nap**
9. The months of the year = magyar.**honap**
10. Fruits = magyar.**gyumolcs**
11. Vegetables = magyar.**zoldseg**
12. Domesticated animals = magyar.**haszonallat**
13. Hungarian wildlife  = magyar.**vad**
14. Fishes of Hungary = magyar.**hal**
15. Birds of Hungary = magyar.**madar**
16. Hungarian names of planets = magyar.**bolygo**
17. Hungarian soup names = magyar.**leves**
18. Hungarian given names M+F  magyar.**keresztnev_v**
19. Hungarian main foods = magyar.**foetel**
20. Hungarian side dishes  = magyar.**koret**
21. Hungarian one-pot meals = magyar.**egytal**
22. Hungarian sweet treats = magyar.**desszert**
23. Hungarian wines =magyar.**bor**
24. Hungarian soft drinks= magyar.**udito**

Dictionary:
1. Hungarian Kings and Reigns = magyar.kiraly
2. Hungarian counties and their administrative centers = magyar.megye_szekhely
3. Hungarian districts, their seats, county = magyar.jaras
4. Hungarian tram lines = magyar.villamos
5. Hunngarian names of Europian capitals, states = magyar.orszag

## Listák használat:

 Főként véletlengenerátorok kiegészítőjeként ajánlom a listákat
 
I recommend it mainly as a supplement to random number generators. 
       
            random.sample()
            utca = random.sample(magyar.utca, k=16) 
            random.choices()
            telepulesek = random.choice(magyar.telepules)
<br>

![Listák](https://raw.githubusercontent.com/kobanya/nevek/master/listak.png)


## Szótárak:
Több adatot tartalmaznak összekapcsolva.

    magyar.kiraly tartalma :   {'király neve' : (uralkodása tól, ig)}
    magyar.megye_szekhely :    {'megye neve' : 'székhelye'}
    magyar.jaras :             {'megye' : (székhely, megye)}
    magyar.villamos:    kulcs  {'viszonylat', indulas, erkezes, menetido, varos}
    magyar.orszag:             {'orszag': 'főváros'}

## Metódus
 1.  A  szótárakból választhatsz véletlenszerű KULCSOT.</br>
    **szotar** = a szótár neve</br>
    **n** = kívánt elemek száma
                    
    szotarbol_veletlen_kulcs(szotar, n)
Pl: </br>
    import magyar</br>
    print(magyar.szotarbol_veletlen_kulcs(magyar.jaras,15)) </br></br>
Eredmény: </br>
    ['Szekszárdi járás', 'Gönci járás', 'Szigetvári járás', 'Mezőkovácsházi járás', 'Bátonyterenyei járás',
    'Körmendi járás', 'Váci járás', 'Edelényi járás', 'Pilisvörösvári járás', 'Kaposvári járás', 'Hódmezővásárhelyi járás',
    'Hatvani járás', 'Törökszentmiklósi járás', 'Putnoki járás', 'Mezőkövesdi járás']
<br>
![ABC rendezés](https://raw.githubusercontent.com/kobanya/nevek/master/jaras_szotar.png)

<br>
2. A listák tartalmának kiíratása tetszőleges elemmel soronként.<br>
    **lst** = a kiírandó lista neve <br>
    **n** = soronkénti elemek száma.  Alapbeállítás, ha üres, 10 elem


        magyar.tordel(lst , n)  

 pl: </br>   
magyar.tordel(magyar.telepules,5) </br>


<br>

![Sima tördelés](https://raw.githubusercontent.com/kobanya/nevek/master/sima_tordel.png)

<br>
3. Listák ABC sorrendbe rendezése, ékezet érzékeny <br>


         magyar.abc(lista):

Használat : </br> </br>
gyumolcs =['Áfonya', 'Eper', 'Alma', 'Meggy','Őszibarack',] </br>
sorban =magyar.abc(gyumolcs) </br>
['Alma', 'Áfonya', 'Eper', 'Meggy', 'Őszibarack']
<br> 
<br>
![ABC](https://raw.githubusercontent.com/kobanya/nevek/master/abc.png)
<br>
4. Listák tördelése "behúzással" </br></br>

        magyar.ftordel(lst,n,'') 
</br></br>
lst = a lista neve</br>
n = hány szó legyen egy sorban</br>
'  ' = a behúzás mértéke ami sztring. '\t' </br>
Kimenetként listát ad vissza. </br></br>

Hasznalat :</br>
formazott_lista= magyar.ftordel(varosok,5,'\t')</br>
print(formazott_lista) vagy f.write(formazott_lista)
</br></br></br>
Minta a használathoz: 
</br>
![ABC rendezés](https://raw.githubusercontent.com/kobanya/nevek/master/abc_rendezes.png)

5. kerekítés egész számra:  </br>

        magyar.fel_kerekit(szam)
        magyar.le_kerekit(szam)


Tizedes számot kerekít egész számra fel vagy le.  </br>
 </br>
![Kerekítés](https://raw.githubusercontent.com/kobanya/nevek/master/kerekites.png)


## Szerző

* Név: Nagy BÉLa
* E-mail:nagy.bela.budapest@gmail.com

## Licenc

Oktatási célra készült, szabadon használható.