def seosta_lapsed_ja_vanemad(lapsed, nimed):
    f = open(lapsed, encoding='UTF-8')
    ff = open(nimed, encoding='UTF-8')
    koodid = []
    for i in f:
        i = i.strip().split()
        koodid.append(i)

    vl = []
    lapsed = set()
    for i in koodid:
        ff.seek(0, 0)
        for n in ff:
            n = n.split()
            if i[0] in n:
                v = n[1] + ' ' + n[2]
            elif i[1] in n:
                l = n[1] + ' ' + n[2]
                lapsed.add(l)
        nim = v, l
        vl.append(nim)

    f.close()
    ff.close()

    lapsevanemad = {}
    for i in lapsed:
        emaisa = set()
        for v in vl:
            if i in v:
                if i != v[0]:
                    emaisa.add(v[0])
        lapsevanemad[i] = emaisa

    return lapsevanemad


nimed = seosta_lapsed_ja_vanemad('lapsed.txt', 'nimed.txt')
lapsed = list(nimed.keys())

for i in lapsed:
    vanemad = ''
    for n in nimed[i]:
        vanemad += n + ' '
    print(i + ':', vanemad)
