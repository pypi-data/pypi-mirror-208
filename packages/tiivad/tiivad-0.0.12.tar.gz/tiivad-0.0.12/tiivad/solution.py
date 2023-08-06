'''
Kasutajalt küsitakse liini pikkust (täisarvuna meetrites)
ja kõrvutiasetsevate postide maksimaalkaugust (täisarvuna
meetrites). Ekraanile väljastatakse, mitu posti on liini
ehitamiseks minimaalselt vaja.
'''

# Kasutame moodulist math ülespoole ümardamise käsku ceil
from math import ceil

# Küsime kasutaja käest andmeid ja teisendame need täisarvudeks
liini_pikkus = int(input("Sisesta elektriliini pikkus täisarvuna meetrites: "))
postide_kaugus = int(input("Sisesta kõrvutasuvate postide maksimaalkaugus: "))

# Valem postide arvu leidmiseks
postide_arv = ceil(liini_pikkus / postide_kaugus) + 1

# Väljastame vastuse ekraanile
print("Liini ehitamiseks läheb vaja minimaalselt", postide_arv, "posti.")

u = "v"

def test(test: int):
    print("a")
    a = test - 3
    # nottest()
    b = 2
    print("c")
    s = []
    v = input("user input 1")
    w = input("user input 1")
    x = input("user input 1")
    y = input("user input 1")
    for i in s:
        pass
    return b

print("u")
test(1)