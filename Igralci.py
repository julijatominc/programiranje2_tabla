from tkinter import*
from Crnobelo import*

import logging
import random
import threading

GLOBINA = 2

SLOVAR_SOSEDOV = {}

def nasprotnik(igralec):
    if igralec == BELI:
        return CRNI
    elif igralec == CRNI:
        return BELI
    else:
        assert False, "neveljaven nasprotnik"

#####################################################################
## Racunalnik

class Racunalnik():
    def __init__(self, Crnobelo, algoritem):
        self.Crnobelo = Crnobelo
        self.algoritem = algoritem # Algoritem, ki izracuna potezo
        self.mislec = None # Vlakno (thread), ki razmislja

    def igraj(self):
        """Igraj potezo, ki jo vrne algoritem."""
        # Tu sprozimo vzporedno vlakno, ki racuna potezo. Ker tkinter ne deluje,
        # ce vzporedno vlakno direktno uporablja tkinter (glej http://effbot.org/zone/tkinter-threads.htm),
        # zadeve organiziramo takole:
        # - pozenemo vlakno, ki poisce potezo
        # - to vlakno nekam zapise potezo, ki jo je naslo
        # - glavno vlakno, ki sme uporabljati tkinter, vsakih 100ms pogleda, ali
        #   je ze bila najdena poteza (metoda preveri_potezo spodaj).
        # Ta resitev je precej amaterska. Z resno knjiznico za GUI bi zadeve lahko
        # naredili bolje (vlakno bi samo sporocilo GUI-ju, da je treba narediti potezo).

        # Naredimo vlakno, ki mu podamo *kopijo* igre (da ne bo zmedel GUIja):
        # logging.debug("Velikost: {0}".format(self.Crnobelo.igra.kopija()))
        self.mislec = threading.Thread(
            target=lambda: self.algoritem.izracunaj_potezo(self.Crnobelo.igra.kopija()))

        # Pozenemo vlakno:
        self.mislec.start()

        # Gremo preverjat, ali je bila najdena poteza:
        self.Crnobelo.canvas.after(100, self.preveri_potezo)

    def preveri_potezo(self):
        """Vsakih 100ms preveri, ali je algoritem ze izracunal potezo."""
        if self.algoritem.poteza is not None:
            # Algoritem je nasel potezo, povleci jo, ce ni bilo prekinitve
            self.Crnobelo.izberi(self.algoritem.poteza)
            #logging.debug("{0}".format(self.Crnobelo.igra.zgodovina))
            #logging.debug("{0}".format(self.Crnobelo.igra.matrika))
            # Vzporedno vlakno ni vec aktivno, zato ga "pozabimo"
            self.mislec = None
        else:
            # Algoritem se ni nasel poteze, preveri se enkrat cez 100ms
            self.Crnobelo.canvas.after(100, self.preveri_potezo)

    def prekini(self):
        # To metodo klice GUI, ce je treba prekiniti razmisljanje.
        if self.mislec:
            logging.debug ("Prekinjamo {0}".format(self.mislec))
            # Algoritmu sporocimo, da mora nehati z razmisljanjem
            self.algoritem.prekini()
            # Pocakamo, da se vlakno ustavi
            self.mislec.join()
            self.mislec = None

    def klik(self, p):
        # Racunalnik ignorira klike
        pass

######################################################################
## Algoritem minimax

class Minimax():
    def __init__(self, globina):
        self.prekiitev = False
        self.igra = None
        self.jaz = None
        self.poteza = None
        self.globina = globina


    ZMAGA = 10000
    VREDNOST_1 = ZMAGA//20
    VREDNOST_2 = ZMAGA//200
    VREDNOST_3 = ZMAGA//2000
    VREDNOST_4 = 0
    NESKONCNO = ZMAGA + 1


    def prekini(self):
        self.prekinitev = True

    #Izracuna vrednost pozicije
    def vrednost_pozicije(self):
        ocena = 0
        for i in self.igra.veljavne_poteze():
            ocena += self.tip_polja(i)

        self.igra.na_vrsti = nasprotnik(self.igra.na_vrsti)

        for i in self.igra.veljavne_poteze():
            ocena -= self.tip_polja(i)

        self.igra.na_vrsti = nasprotnik(self.igra.na_vrsti)

        return ocena


    def izracunaj_potezo(self, igra):
        logging.debug("Igra minimax")
        self.igra = igra
        self.prekinitev = False
        self.jaz = self.igra.na_vrsti
        self.poteza = None
        (poteza, vrednost) = self.minimax(self.globina, True)
        self.jaz = None
        self.igra = None

        if not self.prekinitev:
            # Potezo izvedemo v primeru, da nismo bili prekinjeni
            self.poteza = poteza

    def minimax(self, globina,  maksimiziramo):

        """Glavna metoda minimax."""
        if self.prekinitev:
            # Sporocili so nam, da moramo prekiniti
            logging.debug ("Minimax prekinja, globina = {0}".format(globina))
            return (None, 0)

        if self.igra.je_konec():
            if self.igra.na_vrsti == self.jaz:
                return (None, -Minimax.ZMAGA)
            elif self.igra.na_vrsti == nasprotnik(self.jaz):
                return (None, Minimax.ZMAGA)
            else:
                assert False, "Napaka v koncu igre v Minimaxu."

        else:
            #logging.debug("Sm v minimaxu...")
            if globina == 0:
                return (None, self.vrednost_pozicije())
            else:
                #logging.debug("Globina ni 0...")
                # Naredimo eno stopnjo minimax
                if maksimiziramo:
                    #logging.debug("Je maksimiziramo...")
                    # Maksimiziramo
                    najboljsa_poteza = None
                    vrednost_najboljse = -Minimax.NESKONCNO
                    #logging.debug("{0}".format(self.igra.veljavne_poteze()))
                    for p in self.igra.veljavne_poteze():
                        #logging.debug("Sem v for zanki...")
                        self.igra.povleci_potezo(p)
                        vrednost = self.minimax(globina-1, not maksimiziramo)[1]
                        #logging.debug("Zdej bom razveljavu...")
                        #logging.debug("{0}".format(self.igra.zgodovina))
                        self.igra.razveljavi()
                        if vrednost > vrednost_najboljse:
                            vrednost_najboljse = vrednost
                            najboljsa_poteza = p
                else:
                    #logging.debug("Ni maksimiziramo...")
                    # Minimiziramo
                    najboljsa_poteza = None
                    vrednost_najboljse = Minimax.NESKONCNO
                    #logging.debug("{0}".format(self.igra.veljavne_poteze()))
                    for p in self.igra.veljavne_poteze():
                        self.igra.povleci_potezo(p)
                        vrednost = self.minimax(globina-1, not maksimiziramo)[1]
                        #logging.debug("Zdej bom razveljavu...")
                        #logging.debug("{0}".format(self.igra.zgodovina))
                        self.igra.razveljavi()
                        if vrednost < vrednost_najboljse:
                            vrednost_najboljse = vrednost
                            najboljsa_poteza = p

                assert (najboljsa_poteza is not None), "minimax: izracunana poteza je None"
                return (najboljsa_poteza, vrednost_najboljse)



    #Ustvari seznam sosedov xy
    def sez_sosedov(self, xy):
        if xy in SLOVAR_SOSEDOV:
            return SLOVAR_SOSEDOV[xy]
        else:
            x, y = xy
            sez = []
            sez_polj = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
            for (i, j) in sez_polj:
                if i >= 0 and j >= 0 and  self.igra.velikost() > i and self.igra.velikost() > j:
                    sez.append((i,j))
            SLOVAR_SOSEDOV[xy] = sez
            return sez

    #Funkcija vrne vrednost polja
    def tip_polja(self, xy):
        sosedi = self.sez_sosedov(xy)
        a = self.igra.veljavne_poteze()
        self.igra.na_vrsti = nasprotnik(self.igra.na_vrsti)
        b = self.igra.veljavne_poteze()
        self.igra.na_vrsti = nasprotnik(self.igra.na_vrsti)

        c = True
        for i in sosedi:
            if i in b:
                c = False
                break

        #Polje tipa 1. Polje smo zavzeli mi.
        if xy in a and xy not in b and c:
            return Minimax.VREDNOST_1
        #Polje nam lahko odzame.
        elif xy in a and xy not in b:
            return Minimax.VREDNOST_2
        #Polje je prosto.
        elif xy in a and xy in b:
            return Minimax.VREDNOST_3
        #Polje je neveljavno.
        else:
            return Minimax.VREDNOST_4




######################################################################
## Igralec alfabeta

class Alfabeta():
    def __init__(self):
        # Dodaj se globino.
        self.prekiitev = False
        self.igra = None
        self.jaz = None
        self.poteza = None

    def prekini(self):
        self.prekinitev = True


    def vrednost_pozicije(self):
        pass


    def izracunaj_potezo(self, igra):
        logging.debug("Igra alfabeta")
        self.igra = igra
        self.prekinitev = False
        self.jaz = self.igra.na_vrsti
        self.poteza = None
        poteza = self.alfabeta(igra)

        if not self.prekinitev:
            # Potezo izvedemo v primeru, da nismo bili prekinjeni
            self.poteza = poteza

    def alfabeta(self, igra):
        do_kdaj = False
        while not do_kdaj:
            x =  random.randint(0, (self.igra.velikost()) - 1)
            y =  random.randint(0, (self.igra.velikost()) - 1)
            logging.debug("{0},{1}".format(x,y))
            do_kdaj = self.igra.dovoljeno(x,y)

        return (x,y)

######################################################################
## Igralec clovek

class Clovek():
    def __init__(self, Crnobelo):
        self.Crnobelo = Crnobelo

    def igraj(self):
        # Smo na potezi. Zaenkrat ne naredimo nic, ampak
        # cakamo, da bo uporanik kliknil na plosco. Ko se
        # bo to zgodilo, nas bo Gui obvestil preko metode
        # klik.
        logging.debug("Igra clovek")
        logging.debug("{0}".format(self.Crnobelo.igra.matrika))
        pass

    def prekini(self):
        # To metodo klice GUI, ce je treba prekiniti razmisljanje.
        # Clovek jo lahko ignorira.
        pass

    def klik(self, event):

        # Povlecemo potezo. Ce ni veljavna, se ne bo zgodilo nic.
        x, y = (event.x - 50) // 100, (event.y - 50) // 100
        if x >= 0 and y >= 0 and x < self.Crnobelo.velikost and y <self.Crnobelo.velikost:
            self.Crnobelo.izberi((x,y))
