from tkinter import*
import ast

######################################################################
## Zacetne nastavitve

PRAZNO = 0
JAZ = "Beli"
ON = "Crni"
VELIKOST = 5

######################################################################
## Igra

class tabla():
    def __init__(self, crnobelo):
        # crnobelo rabimo, ker klicemo self.velikost
        self.crnobelo = crnobelo
        self.matrika = [[[True, True, None] for _ in range(self.crnobelo.velikost)] for _ in range(self.crnobelo.velikost)]
        self.na_vrsti = JAZ
        self.konec = False

    # Funkcija, ki preveri, ce je poteza dovoljena.
    def dovoljeno(self, x, y):
        if self.na_vrsti == JAZ and self.matrika[y][x][0]:
            return True
        elif self.na_vrsti == ON and self.matrika[y][x][1]:
            return True
        else:
            return False

    def konec_igre(self):
        if self.na_vrsti == JAZ:
            n = 0
        else:
            n = 1

        for i in range(self.crnobelo.velikost):
            for j in range(self.crnobelo.velikost):
                 if self.matrika[i][j][n]:
                     return False

        return True

######################################################################
## Uporabniski vmesnik

class crnobelo():
    # Ustvarimo tag, da se bomo lahko kasneje sklicevali.
    TAG_KROG = 'krog'


    def __init__(self, master, velikost=VELIKOST):
        self.JAZ = None
        self.ON = None
        self.igra = None

        # Definira vrednosti.
        self.velikost = velikost
        self.canvas = Canvas(master, width=100*(self.velikost+1), height=100*(self.velikost +1))
        self.canvas.grid(row=1, column=0)

        # Na canvas narise zacetno polje.
        self.narisi()

        # Povezemo klik z dogodkom.
        self.canvas.bind("<Button-1>", self.plosca_klik)

        # Ustvarimo napis, ki nas obvesca o dogajanju.
        self.napis = StringVar()
        label_napis = Label(master, textvariable=self.napis)
        label_napis.grid(row=0, column=0)

        # Glavni menu.
        menu = Menu(master)
        master.config(menu=menu)

        # Dodamo moznosti v menu.
        file_menu = Menu(menu)
        menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Nova igra", command=self.nova_igra)
        file_menu.add_command(label="Shrani", command=self.shrani)
        file_menu.add_command(label="Odpri", command=self.odpri)
        file_menu.add_separator()
        file_menu.add_command(label="Izhod", command=master.destroy)

        settings_menu = Menu(menu)
        menu.add_cascade(label="Velikost", menu=settings_menu)
        settings_menu.add_command(label="5", command= lambda: self.nova_igra(None, None, 5))
        settings_menu.add_command(label="6", command= lambda: self.nova_igra(None, None, 6))
        settings_menu.add_command(label="7", command= lambda: self.nova_igra(None, None, 7))
        settings_menu.add_command(label="8", command= lambda: self.nova_igra(None, None, 8))
        settings_menu.add_command(label="9", command= lambda: self.nova_igra(None, None, 9))

        self.zacni_igro()

    # Funkcija za risanje sahovnice.
    def narisi(self):
        for i in range(self.velikost+1):
            self.canvas.config(width=100*(self.velikost+1), height=100*(self.velikost +1))
            self.canvas.create_line(50, i*100 + 50,(self.velikost*100)+50,i*100 +50)
            self.canvas.create_line(i*100 +50, 50 , i*100 +50, (self.velikost*100) +50)

    # Funkcija, ki zacne igro.
    def zacni_igro(self, beli=None, crni=None):
        if not beli:
            beli = clovek(self)
        if not crni:
            crni = clovek(self)

        self.igra = tabla(self)
        self.nova_igra(beli, crni)


    # Funkcija, ki ustvari novo igro.
    def nova_igra(self, beli=None, crni=None, velikost=None):

        self.prekini_igralce()

        if  velikost:
            self.velikost = velikost
            self.canvas.delete("all")
            self.narisi()
        else:
            self.canvas.delete(crnobelo.TAG_KROG)

        if beli and crni:
            self.JAZ = beli
            self.ON = crni

        self.igra.matrika = [[[True, True, None] for _ in  range(self.velikost)] for _ in range(self.velikost)]
        self.napis.set("")
        self.igra.na_vrsti = JAZ

    # Funkcija, ki preda dogodek na plosci razredu igralca, ki je storil to potezo
    def plosca_klik(self, event):
        if self.igra.na_vrsti == JAZ:
            self.JAZ.klik(event)
        elif self.igra.na_vrsti == ON:
            self.ON.klik(event)
        else:
            pass

    # Funkcija, ki glede na igralca na vrsti in na njegovo dejanje naredi potezo
    def izberi(self, event):
        # Preveri, ce je konec igre. V primeru, da je konec, nocemo vec dogajanja na plosci.
        if not self.igra.konec:
            self.napis.set("")
            x, y = (event.x - 50) // 100, (event.y - 50) // 100
            if x >= 0 and y >= 0 and x < self.velikost and y <self.velikost:
                # Preveri, ce je poteza dovoljena.
                if self.igra.dovoljeno(x, y):
                    if self.igra.na_vrsti == JAZ:
                        # Spremeni matriko, v kateri imamo zapisano katere poteze so mozne.
                        self.spremeni_matriko(x, y, 1)
                        # Na potezi je nasprotnik.
                        self.igra.na_vrsti = ON
                        # Narise krog.
                        self.canvas.create_oval(x * 100 + 60, y * 100 + 60, x * 100 + 140, y * 100 + 140, tag=crnobelo.TAG_KROG)
                    else:
                        self.spremeni_matriko(x, y, 0)
                        self.igra.na_vrsti = JAZ
                        self.canvas.create_oval(x * 100 + 60, y * 100 + 60, x * 100 + 140, y * 100 + 140, fill="black", tag=crnobelo.TAG_KROG)

                    if self.igra.konec_igre():
                        if self.igra.na_vrsti == JAZ:
                            self.igra.na_vrsti = ON
                        else:
                            self.igra.na_vrsti = JAZ
                        self.napis.set("Konec igre! Zmagal je {0}!".format(self.igra.na_vrsti))
                        self.igra.konec = True

                else:
                    self.napis.set("Neveljavna poteza!")
        print(self.igra.konec_igre())


    # Funkcija, ki shrani igro v datoteko.
    def shrani(self):
        ime = filedialog.asksaveasfilename()
        if ime == "":
            return
        with open(ime, "wt", encoding="utf8") as f:
            print(self.igra.matrika, file=f)
            print(self.igra.na_vrsti, file=f)
            print(self.velikost, file=f)

    # Funkcija, ki nalozi igro iz datoteke.
    def odpri(self):
        ime = filedialog.askopenfilename()
        s = open(ime, encoding="utf8")
        sez = s.readlines()
        s.close

        self.igra.matrika = ast.literal_eval(sez[0].strip())
        KDO = sez[1].strip()
        velikost = sez[2].strip()

        self.nova_igra(velikost)

        if KDO == "Beli":
            self.igra.na_vrsti = JAZ
        else: self.igra.na_vrsti = ON

        for i in range(self.velikost):
            for j in range(self.velikost):
                if self.matrika[i][j][2] == "Beli":
                    self.canvas.create_oval(i * 100 + 60, j * 100 + 60, i * 100 + 140, j * 100 + 140)
                if self.igra.matrika[i][j][2] == "Crni":
                    self.canvas.create_oval(i * 100 + 60, j * 100 + 60, i * 100 + 140, j* 100 + 140, fill="black")




    # Funkcija, ki potezo zapise v matriko in hkrati doloci katere poteze so mogoce.
    def spremeni_matriko(self, x, y, n):
        self.igra.matrika[y][x][0] = False
        self.igra.matrika[y][x][1] = False
        self.igra.matrika[y][x][2] = self.igra.na_vrsti

        if y-1 >= 0:
            self.igra.matrika[y-1][x][n] = False
        else:
            pass

        try:
            self.igra.matrika[y+1][x][n] = False
        except:
            pass

        if x-1 >= 0:
            self.igra.matrika[y][x-1][n] = False
        else:
            pass

        try:
            self.igra.matrika[y][x+1][n] = False
        except:
            pass

    # Funkcija, ki prekine igralce
    def prekini_igralce(self):
        if self.JAZ:
            self.JAZ.prekini()
        if self.ON:
            self.ON.prekini()

######################################################################
## Igralec minimax

class minimax():
    pass

######################################################################
## Igralec alfabeta

class alfabeta():
    pass

######################################################################
## Igralec clovek

class clovek():
    def __init__(self, CRNOBELO):
        self.CRNOBELO = CRNOBELO

    def igraj(self):
        # Smo na potezi. Zaenkrat ne naredimo nic, ampak
        # cakamo, da bo uporanik kliknil na plosco. Ko se
        # bo to zgodilo, nas bo Gui obvestil preko metode
        # klik.
        pass

    def prekini(self):
        # To metodo klice GUI, ce je treba prekiniti razmisljanje.
        # Clovek jo lahko ignorira.
        pass

    def klik(self, p):
        # Povlecemo potezo. Ce ni veljavna, se ne bo zgodilo nic.
        self.CRNOBELO.izberi(p)

######################################################################
## Glavni program

if __name__ == "__main__":
    # Naredimo glavno okno in nastavimo ime
    root = Tk()
    root.title("Crnobelo")
    # Naredimo objekt razreda Gui in ga spravimo v spremenljivko,
    aplikacija = crnobelo(root)
    # Kontrolo prepustimo glavnemu oknu. Funkcija mainloop neha
    # delovati, ko okno zapremo.
    root.mainloop()