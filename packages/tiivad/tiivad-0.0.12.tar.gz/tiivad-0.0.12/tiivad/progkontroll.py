from edutest import *
from inspect import signature
import ast
import os
from copy import deepcopy
import datetime


# Lõpetab automaatkontrollimise (st genereerib erindi)
def lõpeta(teade, väljund=""):
    if väljund != "":
        if teade[-1] != '\n':
            teade += '\n'
        teade += "\nProgrammi väljund oli:" + quote_text_block(väljund)
    raise AssertionError(teade)


# Abifunktsioon tekstide "arv+ühik" väljastamiseks
def arvsõne(n, ainsus, mitmus):
    s = str(n) + " "
    if n == 1:
        s += ainsus
    else:
        s += mitmus
    return s


# Abifunktsioon järjendi liikmete väljastamiseks
def jadasõne(a):
    s = ""
    for i in range(len(a)):
        if i > 0:
            s += " "
        s += str(a[i])
        if i < len(a) - 2:
            s += ","
        elif i == len(a) - 2:
            s += " ja"
    return s


# Kontrollib, kas sisend on arv
def on_arv(s):
    try:
        float(str(s))
        return True
    except ValueError:
        return False
    except TypeError:
        return False


# Kontrollib, kas sisend on täisarv
def on_täisarv(s):
    try:
        int(str(s))
        return True
    except ValueError:
        return False
    except TypeError:
        return False


# Kontrollib, kas antud nimega programm on olemas
def progolemasolu(programminimi):
    assert os.path.isfile(programminimi), "Ei leia faili %s." % programminimi
    assert os.path.getsize(programminimi) > 0, "Failil %s puudub sisu." % programminimi


# Programmi sisendparameetrite arvu kontrollimine ja teadete väljastamine.
# Veatekst on täiendav info kasutajale vea korral.
def progsisendiarvukontroll(tegelik_sisendite_arv, oodatav_sisendite_arv, veatekst=""):
    if tegelik_sisendite_arv != oodatav_sisendite_arv:
        if tegelik_sisendite_arv == 0 and oodatav_sisendite_arv > 0:
            teade = "Programm ei küsinud sisendeid.\n"
            teade += "Programm peaks küsima sisendit kasutajalt."
            lõpeta(teade)
        elif tegelik_sisendite_arv > 0 and oodatav_sisendite_arv == 0:
            teade = "Programm küsis sisendit.\n"
            teade += "Programm ei tohiks kasutajalt ühtegi sisendit küsida."
            lõpeta(teade)
        elif float('Inf') > tegelik_sisendite_arv > 0 and oodatav_sisendite_arv > 0:
            teade = "Programm küsis "
            teade += ("vähem" if tegelik_sisendite_arv < oodatav_sisendite_arv else "rohkem")
            teade += " sisendeid, kui oleks pidanud.\n"
            teade += "Programm küsis " + arvsõne(tegelik_sisendite_arv, "sisendit", "sisendit") \
                     + ", aga oleks pidanud küsima " + arvsõne(oodatav_sisendite_arv, "sisendit", "sisendit") + ".\n"
            teade += veatekst
            lõpeta(teade)
        elif tegelik_sisendite_arv == float('Inf') and oodatav_sisendite_arv > 0:
            teade = "Programm küsis rohkem sisendeid, kui oleks pidanud.\n"
            teade += "Programm peaks küsima ainult " + arvsõne(oodatav_sisendite_arv, "sisendit", "sisendit") + ".\n"
            teade += veatekst
            lõpeta(teade)


# Täidab programmi etteantud sisenditega, kontrollib ka sisendite arvu.
def täidaprog(programminimi, sisendid, oodatav_sisendite_arv, veatekst=""):
    try:
        globs, cap = run_script(programminimi, sisendid)
    except OutOfInputsError:
        tegelik_sisendite_arv = float('Inf')
    else:
        tegelik_sisendite_arv = len(sisendid) - len(cap.get_remaining_inputs())
    progsisendiarvukontroll(tegelik_sisendite_arv, oodatav_sisendite_arv, veatekst)
    return globs, cap


# Kontrollib, kas programmis on olemas antud nime ja parameetrite arvuga funktsioon.
def funksignatuur(globs, funktsiooninimi, oodatav_parameetrite_arv, veatekst=""):
    if funktsiooninimi not in globs:
        lõpeta("Ei leia programmist funktsiooni '" + str(funktsiooninimi) + "'.")

    tegelik_parameetrite_arv = len(signature(globs[funktsiooninimi]).parameters)
    if tegelik_parameetrite_arv != oodatav_parameetrite_arv:
        teade = "Funktsioonil '" + str(funktsiooninimi) + "' on " + \
                arvsõne(tegelik_parameetrite_arv, "parameeter", "parameetrit") + ", " \
                                                                                 "aga peaks olema " + \
                arvsõne(oodatav_parameetrite_arv, "parameeter", "parameetrit") + "."
        # Parameetrite kirjeldus
        if veatekst != "":
            teade += "\n" + veatekst
        lõpeta(teade)


# Funktsiooni sisendparameetrite arvu kontrollimine ja teadete väljastamine.
def funksisendiarvukontroll(funktsiooninimi, tegelik_sisendite_arv, oodatav_sisendite_arv, veatekst=""):
    if tegelik_sisendite_arv != oodatav_sisendite_arv:
        if tegelik_sisendite_arv == 0 and oodatav_sisendite_arv > 0:
            teade = "Funktsioon '" + str(funktsiooninimi) + "' ei küsinud sisendeid.\n"
            teade += "Funktsioon peaks küsima sisendit kasutajalt."
            lõpeta(teade)
        elif tegelik_sisendite_arv > 0 and oodatav_sisendite_arv == 0:
            teade = "Funktsioon '" + str(funktsiooninimi) + "' küsis "
            teade += ("sisendit" if tegelik_sisendite_arv == 1 else "sisendeid") + ".\n"
            teade += "Funktsioon ei tohiks kasutajalt ühtegi sisendit küsida, andmed tuleks talle ette anda argumentidena."
            lõpeta(teade)
        elif float('Inf') > tegelik_sisendite_arv > 0 and oodatav_sisendite_arv > 0:
            teade = "Funktsioon '" + str(funktsiooninimi) + "' küsis "
            teade += ("vähem" if tegelik_sisendite_arv < oodatav_sisendite_arv else "rohkem")
            teade += " sisendeid, kui oleks pidanud.\n"
            teade += "Funktsioon küsis " + arvsõne(tegelik_sisendite_arv, "sisendit", "sisendit") \
                     + ", aga oleks pidanud küsima " + arvsõne(oodatav_sisendite_arv, "sisendit", "sisendit") + ".\n"
            teade += veatekst
            lõpeta(teade)
        elif tegelik_sisendite_arv == float('Inf') and oodatav_sisendite_arv > 0:
            teade = "Funktsioon '" + str(funktsiooninimi) + "' küsis "
            teade += "rohkem sisendeid, kui oleks pidanud.\n"
            teade += "Funktsioon peaks küsima ainult " + arvsõne(oodatav_sisendite_arv, "sisendit", "sisendit") + ".\n"
            teade += veatekst
            lõpeta(teade)


# Täidab funktsiooni etteantud argumentide ja sisenditega, kontrollib ka sisendite arvu.
def täidafunk(funktsioon, argumendid, sisendid, oodatav_sisendite_arv, veatekst=""):
    try:
        with IOCapturing(sisendid) as cap:
            tegelik_tulemus = funktsioon(*argumendid)
    except OutOfInputsError:
        tegelik_sisendite_arv = float('Inf')
    else:
        tegelik_sisendite_arv = len(sisendid) - len(cap.get_remaining_inputs())
    funksisendiarvukontroll(funktsioon.__name__, tegelik_sisendite_arv, oodatav_sisendite_arv, veatekst)
    return tegelik_tulemus, cap


# Kontrollib, kas programm pöördub funktsiooni poole.
def progpöördub(programminimi, funktsiooninimi):
    with open(programminimi, encoding='utf-8') as f:
        programmisisu = f.read()
        süntaksipuu = ast.parse(programmisisu)
        if type(funktsiooninimi) == str:
            kontrollitavad = [funktsiooninimi]
        elif type(funktsiooninimi) == list:
            kontrollitavad = funktsiooninimi
        for tipp in ast.walk(süntaksipuu):
            if isinstance(tipp, ast.Call):
                if 'func' in tipp._fields:
                    if 'id' in tipp.func._fields:
                        for i in range(len(kontrollitavad)):
                            if tipp.func.id == kontrollitavad[i]:
                                return True
                    if 'attr' in tipp.func._fields:
                        for i in range(len(kontrollitavad)):
                            if tipp.func.attr == kontrollitavad[i]:
                                return True
    return False


# Kontrollib, kas funktsioon pöördub funktsiooni poole.
def funkpöördub(programminimi, funktsiooninimi, kontrollitavnimi):
    with open(programminimi, encoding='utf-8') as f:
        programmisisu = f.read()
        süntaksipuu = ast.parse(programmisisu)
        if type(kontrollitavnimi) == str:
            kontrollitavad = [kontrollitavnimi]
        elif type(kontrollitavnimi) == list:
            kontrollitavad = kontrollitavnimi
        for tipp in ast.walk(süntaksipuu):
            if isinstance(tipp, ast.FunctionDef) and tipp.name == funktsiooninimi:
                for alamtipp in ast.walk(tipp):
                    if isinstance(alamtipp, ast.Call):
                        if 'func' in alamtipp._fields:
                            if 'id' in alamtipp.func._fields:
                                for i in range(len(kontrollitavad)):
                                    if alamtipp.func.id == kontrollitavad[i]:
                                        return True
                            if 'attr' in alamtipp.func._fields:
                                for i in range(len(kontrollitavad)):
                                    if alamtipp.func.attr == kontrollitavad[i]:
                                        return True
    return False


# Annab veateate, kui programm ei kasuta funktsiooni.
def progfunkkasutamine(programminimi, funktsiooninimi):
    if not progpöördub(programminimi, funktsiooninimi):
        teade = "Programm ei kasuta funktsiooni '" + funktsiooninimi + "'.\n"
        teade += "Väljund tuleks arvutada programmis defineeritud funktsiooni '" + funktsiooninimi + "' abil."
        lõpeta(teade)


# Kontrollib, kas programm kasutab moodulit
def kasutabmoodulit(programminimi, moodulinimi):
    with open(programminimi, encoding='utf-8') as f:
        programmisisu = f.read()
    süntaksipuu = ast.parse(programmisisu)
    if type(moodulinimi) == str:
        kontrollitavad = [moodulinimi]
    elif type(moodulinimi) == list:
        kontrollitavad = moodulinimi
    for tipp in ast.walk(süntaksipuu):
        if isinstance(tipp, ast.Import):
            if 'names' in tipp._fields:
                for nimi in tipp.names:
                    if 'name' in nimi._fields:
                        for i in range(len(kontrollitavad)):
                            if nimi.name == kontrollitavad[i]:
                                return True
        if isinstance(tipp, ast.ImportFrom):
            if 'module' in tipp._fields:
                for i in range(len(kontrollitavad)):
                    if tipp.module == kontrollitavad[i]:
                        return True
    return False


# Annab veateate, kui programm ei kasuta moodulit.
def moodulikasutamine(programminimi, moodulinimi):
    if not kasutabmoodulit(programminimi, moodulinimi):
        teade = "Programm ei kasuta moodulit '" + moodulinimi + "'.\n"
        lõpeta(teade)


# Kontrollib, kas funktsioon püüab tagastamise asemel väärtust väljastada.
def tühiprintteade(programminimi, funktsiooninimi):
    teade = "Funktsioon '" + str(funktsiooninimi) + "' ei tagastanud väärtust."
    if funkpöördub(programminimi, funktsiooninimi, "print"):
        teade += "\nFunktsioon peaks väärtuse tagastama, mitte väljastama."
    lõpeta(teade)


# Kontrollib, kas funktsioon tagastas õiget tüüpi väärtuse.
def funktüüp(funktsiooninimi, tegelik_tulemus, õige_tüüp):
    if type(tegelik_tulemus) != õige_tüüp:
        teade = "Funktsioon '" + str(funktsiooninimi) + "' tagastas väärtuse, mis ei ole "
        if õige_tüüp == str:
            teade += "sõne"
        elif õige_tüüp == list:
            teade += "järjend"
        elif õige_tüüp == int:
            teade += "täisarv"
        elif õige_tüüp == bool:
            teade += "tõeväärtus"
        elif õige_tüüp == dict:
            teade += "sõnastik"
        elif õige_tüüp == tuple:
            teade += "ennik"
        else:
            teade += "õiget tüüpi"
        teade += ".\n"
        teade += "Tagastatud väärtus oli "
        if type(tegelik_tulemus) == str: teade += "'"
        teade += str(tegelik_tulemus)
        if type(tegelik_tulemus) == str: teade += "'"
        teade += "."
        lõpeta(teade)

