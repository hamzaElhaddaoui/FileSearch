import os
from threading import *
from threading import RLock
from tkinter import *
from tkinter import filedialog
from tkinter import ttk

from whoosh import qparser
from whoosh import scoring
from whoosh.fields import Schema, TEXT, ID
from whoosh.index import create_in
from whoosh.index import open_dir
from whoosh.qparser import QueryParser


def addInIndex(writer,root,progressBare):
    nbIndexed=0
    print("---------------------------------------------")
    i=1
    for root, dirs, files in os.walk(root, topdown=True):
        for name in files:
            path = os.path.join(root, name)
            extension = name.split(".")[len(name.split(".")) - 1]
            print(path)
            print(name)
            text = ""
            if extension.endswith(('txt', 'sql', 'doc')):
                fp = open(path, 'r')
                if fp.mode == 'r':
                    try:
                        text = fp.read()
                    except UnicodeDecodeError:
                        print("fichier contients des caracters ne peut pas etre lire")
                fp.close()
            nbIndexed += 1
            writer.add_document(title=name, path=path, content=text, tags=text, extension=extension)
            if i <= 16000 and (i%200) == 0:
               progressBare["value"] = i/200
            i = i+1

        for name in dirs:
            print("*****************************")
            print(os.path.join(root, name))
    print("---------------------------------------------")
    print(nbIndexed)

verrou = RLock()

def createSearchableData(root, progressbar):
    '''
    Schema definition: title(name of file), path(as ID), content(indexed
    but not stored),textdata (stored text content)
    '''

    with verrou:
        schema = Schema(title=TEXT(stored=True), path=ID(stored=True), content=TEXT, tags=TEXT(stored=True), extension=TEXT(stored=True))

        if not os.path.exists("indexdir"):
            os.mkdir("indexdir")

    # Creating a index writer to add document as per schema
        ix = create_in("indexdir", schema)

        writer = ix.writer()
        addInIndex(writer, root, progressbar)
        progressbar["value"] = 90
        writer.commit()
        progressbar["value"] = 100
        print("commit done!")

def searchDataByName(name, treeFrame, maxAff, itemTrouve, tempsExecution, trierPar):
    for i in treeFrame.get_children():
        treeFrame.delete(i)

    try:
        maxAffInt = int(maxAff)
        maxAffInt = maxAffInt if maxAffInt > 0 else None
    except ValueError:
        maxAffInt = None

    ix = open_dir("indexdir")

    # query_str is query string
    query_str = name+'*'
    print("Le nom a chercher ", name)
    # Top 'n' documents as result
    # topN = 3

    with ix.searcher(weighting=scoring.Frequency) as searcher:
        query = QueryParser("title", ix.schema).parse(query_str)
        if (trierPar=="Type"):
            results = searcher.search(query, terms=True, limit=maxAffInt, sortedby="extension")
            print("sortedby extension")
        elif (trierPar=="Nom"):
            results = searcher.search(query, terms=True, limit=maxAffInt, sortedby="title")
            print("sortedby name")
        else:
            results = searcher.search(query, terms=True, limit=maxAffInt)
            print("sortedBy score")

        if(maxAffInt!=None):
            max = maxAffInt if maxAffInt < len(results) else len(results)
        else:
            max = len(results)

        if len(results) > 0:
            itemTrouve['text'] = "Item trouvé : "+str(len(results))
            tempsExecution['text'] = "Temps d'execution : " + str(results.runtime) + " s"
            for i in range(max):
                treeFrame.insert("", "end", text="", values=(results[i]['title'], results[i]['path'], results[i]['extension'], results[i]['tags']))
                print("File Name: " + results[i]['title'], "Path: "+results[i]['path'], "Extension: " + results[0]['extension'])
        else:
            print("Aucun resultat trouvé !")

def searchDataByType(type, treeFrame, maxAff, itemTrouve, tempsExecution, trierPar):
    for i in treeFrame.get_children():
        treeFrame.delete(i)

    try:
        maxAffInt = int(maxAff)
        maxAffInt = maxAffInt if maxAffInt > 0 else None
    except ValueError:
        maxAffInt = None

    ix = open_dir("indexdir")

    query_str = type
    print('Le type a chercher ', type)
    with ix.searcher(weighting=scoring.Frequency) as searcher:
       query= QueryParser("extension", ix.schema).parse(query_str)

       if (trierPar == "Type"):
           results = searcher.search(query, terms=True, limit=maxAffInt, sortedby="extension")
           print("sortedby extension")
       elif (trierPar == "Nom"):
           results = searcher.search(query, terms=True, limit=maxAffInt, sortedby="title")
           print("sortedby name")
       else:
           results = searcher.search(query, terms=True, limit=maxAffInt)
           print("sortedBy score")

       if(maxAffInt!=None):
           max = maxAffInt if maxAffInt < len(results) else len(results)
       else:
           max = len(results)
       if len(results) > 0:
           itemTrouve['text'] = "Item trouvé : " + str(len(results))
           tempsExecution['text'] = "Temps d'execution : " + str(results.runtime) + " s"
           for i in range(max):
               treeFrame.insert("", "end", text="", values=(results[i]['title'], results[i]['path'], results[i]['extension'],results[i]['tags']))

               print("File Name: " + results[i]['title'], "Path: " + results[i]['path'], "Contenu: "+results[i]['tags'],
                     "Extension: " + results[i]['extension'])
           print(results)
       else:
            print("Aucun resultat trouvé !")


def searchByContent(content, treeFrame, maxAff, itemTrouve, tempsExecution, trierPar):
    for i in treeFrame.get_children():
        treeFrame.delete(i)

    try:
        maxAffInt = int(maxAff)
        maxAffInt = maxAffInt if maxAffInt> 0 else None
    except ValueError:
        maxAffInt = None

    ix = open_dir("indexdir")

    query_str = content
    print('Le contenue a recherche est ', content)
    with ix.searcher(weighting=scoring.Frequency) as searcher:
        query = QueryParser("tags", ix.schema).parse(query_str)

        if (trierPar=="Type"):
            results = searcher.search(query, terms=True, limit=maxAffInt, sortedby="extension")
            print("sortedby extension")
        elif (trierPar=="Nom"):
            results = searcher.search(query, terms=True, limit=maxAffInt, sortedby="title")
            print("sortedby name")
        else:
            results = searcher.search(query, terms=True, limit=maxAffInt)
            print("sortedBy score")

        if(maxAffInt != None):
            max = maxAffInt if maxAffInt < len(results) else len(results)
        else:
            max=len(results)
        itemTrouve['text'] = "Item trouvé : " + str(len(results))
        tempsExecution['text'] = "Temps d'execution : " + str(results.runtime) + " s"
        if len(results) > 0:
            for i in range(max):
                treeFrame.insert("", "end", text="", values=(
                results[i]['title'], results[i]['path'], results[i]['extension'], results[i]['tags']))
                print("File Name: " + results[i]['title'], "Path: " + results[i]['path'], "Contenu: " + results[i]['tags'],
                     "Extension: " + results[i]['extension'])
                print(results)

        else:
            print("Aucun resultat trouvé !")


def searchDataByNameAndType(name, type):
    ix = open_dir("indexdir")
    query_str = name+'* '+type

    with ix.searcher(weighting=scoring.Frequency) as searcher:
        query = qparser.MultifieldParser(["title", "extension"], ix.schema).parse(query_str)
        results = searcher.search(query, limit=None)
        if len(results) > 0:
            for i in range(len(results)):
                print("File Name: " + results[i]['title'], "Path: " + results[i]['path'],
                      "Extension: " + results[i]['extension'])

        else:
            print("Aucun resultat trouvé !")


def chercher(input,type, treeFrame, maxAff, itemTrouve, tempsExecution, buttonExp, trierPar):
    buttonExp['state'] = "disabled"
    if type == "Nom fichier":
        print(input.get())
        searchDataByName(input.get(), treeFrame, maxAff, itemTrouve, tempsExecution, trierPar)
    elif type == "Type fichier":
        searchDataByType(input.get(), treeFrame, maxAff, itemTrouve, tempsExecution, trierPar)
    elif type == "Contenu":
        searchByContent(input.get(), treeFrame, maxAff, itemTrouve, tempsExecution, trierPar)

class GenererBD(Thread):
    def __init__(self, root, bottonUpdate, bottonChercher, bareProgress):
        Thread.__init__(self)
        self.path = root
        self.bottonUpdate = bottonUpdate
        self.bottonChercher = bottonChercher
        self.bareProgress = bareProgress
    def run(self):
        self.bareProgress["value"] = 0
        self.bareProgress["maximum"] = 100
        self.bottonUpdate["state"] = "disabled"
        self.bottonChercher["state"] = "disabled"

        createSearchableData(self.path, self.bareProgress)
        self.bottonUpdate["state"] = "normal"
        self.bottonChercher["state"] = "normal"
        fichierPw = open("DirectoryIndexed.txt", "w")
        fichierPw.write(self.path)
        fichierPw.close()


def updateData():
    createSearchableData(root)

def browse_button(buttonUpdate, labelPath):
    #global folder_path
    filename = filedialog.askdirectory()
    #folder_path.set(filename)
    print(filename)
    labelPath['text'] = filename
    root = filename
    print(root)
    buttonUpdate['state'] = "normal"



def afficher_graphique():

    fenetre = Tk()
    fenetre.title('Search file')
    fenetre.minsize(925, 650)
    fenetre.resizable(0, 0)

    recherche = Frame(fenetre, width=500, height=200, borderwidth=2)
    recherche.pack()

    rechercheLabel=Label(recherche, text="La recherche", anchor="w", font=("Courier", 14), height=2)
    rechercheLabel.grid(row=0, column=0)
    champ_label = Label(recherche, text="Entrez le terme à chercher :", anchor="w", width=20)
    champ_label.grid(row=1, column=0)
    # champ_label.pack(side="top", fill=Y)
    var_text = StringVar()
    ligne_text = Entry(recherche, textvariable=var_text, width=60)
    print(var_text)
    ligne_text.grid(row=1, column=1)
    margeLabel=Label(recherche, text="TopN :", anchor="w", width=8)
    margeLabel.grid(row=1, column=2)
    var_topN=StringVar()
    topN_entry=Entry(recherche, textvariable=var_topN, width=15)
    topN_entry.grid(row=1, column=3)
    boutton_chercher = Button(recherche, text="Chercher", command=lambda: chercher(var_text, tkvar.get(), fileTable, var_topN.get(),
                                                                                   itemTrouveValeur, tempsExecutionValeur, label1, typetrier.get()))
    boutton_chercher.grid(row=1, column=5)

    # Create a Tkinter variable
    tkvar = StringVar()
    # Dictionary with options
    choices = {'Nom fichier', 'Type fichier', 'Contenu'}
    tkvar.set('Nom fichier')
    popupMenu = OptionMenu(recherche, tkvar, *choices)  # set the default option
    popupMenu.grid(row=1, column=4)

    itemTrouveValeur = Label(recherche, text="", anchor="w")
    itemTrouveValeur.grid(row=2, column=0)

    tempsExecutionValeur = Label(recherche, text="", anchor="w")
    tempsExecutionValeur.grid(row=2, column=1)

    trierLabel=Label(recherche, text="Triez par :", anchor="w")
    trierLabel.grid(row=2, column=2)

    # Create a Tkinter variable
    typetrier = StringVar()
    # Dictionary with options
    choicesType = {'Fréquence', 'Date', 'Type', 'Nom'}
    typetrier.set('Fréquence')
    popupMenu = OptionMenu(recherche, typetrier, *choicesType)  # set the default option
    popupMenu.grid(row=2, column=3)


    indexation = Frame(fenetre, width=500, height=200, borderwidth=2)
    indexation.pack()



    labelIndexation=Label(indexation, text="L'indexation", anchor="w", font=("Courier",14), width=18, height=2)
    labelIndexation.grid(row=0, column=0)

    labelChemin=Label(indexation, text="Chemin de dossier Indexé: ", anchor="w", width=28, height=2)
    labelChemin.grid(row=1, column=0)
    labelPath=Label(indexation, text="", anchor="w", width=35)
    labelPath.grid(row=1, column=1)
    labelPath['text'] = root

    button_updateDb = Button(indexation, text="Update BD", command=lambda: GenererBD(labelPath['text'], button_updateDb, boutton_chercher, bareProgress).start(), width=17)
    button_updateDb.grid(row=1, column=5)
    button_updateDb['state'] = "disabled"

    button2 = Button(indexation, text="Browse", command=lambda: browse_button(button_updateDb, labelPath))
    button2.grid(row=1, column=4)

    bareProgress = ttk.Progressbar(indexation, orient=HORIZONTAL, length=200)
    bareProgress.grid(row=1, column=6)

    # link function to change dropdown
    #tkvar.trace('w', change_dropdown)
    treeviewFrame = Frame(fenetre)
    treeviewFrame.pack()

    fileTable = ttk.Treeview(treeviewFrame, height=17)
    fileTable['columns'] = ("Nom fichier", "Path", "Extension", "Contenu")
    fileTable.grid(row=2, column=1, columnspan=5, pady=20)
    fileTable.heading("#0", text="", anchor="w")

    def selectItem(event):
        global pathfile
        curItem = fileTable.focus()
        label1['state'] = "normal"
        obj = fileTable.item(curItem)
        print(obj.get("values")[1])
        pathfile = obj.get("values")[1].replace("\\"+obj.get("values")[0], "")
        print(pathfile)

    fileTable.bind('<ButtonRelease-1>', selectItem)
    fileTable.column("#0", anchor="center", width=5, stretch=NO)
    fileTable.heading("Nom fichier", text="Nom fichier", anchor="w")
    fileTable.column("Nom fichier", anchor="w", width=240)
    fileTable.heading("Path", text="Path", anchor="w")
    fileTable.column("Path", anchor="w", width=240)
    fileTable.heading("Extension", text="Extension", anchor="w")
    fileTable.column("Extension", anchor="w", width=90)
    fileTable.heading("Contenu", text="Contenu", anchor="w")
    fileTable.column("Contenu", anchor="w", width=240)
    EmployViewScrollbar = ttk.Scrollbar(treeviewFrame, orient="vertical", command=fileTable.yview)
    fileTable.configure(yscroll=EmployViewScrollbar.set)
    EmployViewScrollbar.grid(row=2, column=6, sticky="ns")

    def open():
        tmp = "F:/Ensias/ENSIAS - 2A/9raya S3\Administration Unix\TP\tpunix_romadi1.txt"

        gotoFenetre='start "" "'+pathfile+'"'
        print(gotoFenetre)
        os.system(gotoFenetre)


    label1 = Button(fenetre, text="Ouvrir le dossier contenant le fichier", anchor="w", fg="red", font=("Courier", 9, "bold"), command=open)
    label1.pack()
    label1['state'] = "disabled"


    fenetre.mainloop()


fichierP = open("DirectoryIndexed.txt", "r")
root = fichierP.read()
fichierP.close()

# createSearchableData(root)
# searchData()
if len(sys.argv) < 2 or len(sys.argv) > 5:

    print("Please use proper format")
    print("Use < fileSearchTest -c > to create database file")
    print("Use < fileSearchTest -content content > to search by content")
    print("Use < fileSearchTest -name name_file > to search file")
    print("Use < fileSearchTest -type extension > to search by extension")
    # print("Use < fileSearchTest -content term_to_search > to search by content")
    print(len(sys.argv))
    print(sys.argv[1])
    print(sys.argv[3])
"""
elif sys.argv[1] == '-c':

    createSearchableData(root, "create")

elif len(sys.argv) == 3 and sys.argv[1] == '-name':
    searchDataByName(sys.argv[2])

elif len(sys.argv) == 3 and sys.argv[1] == '-type':
    searchDataByType(sys.argv[2])
elif len(sys.argv) == 3 and sys.argv[1] == '-content':
    searchByContent(sys.argv[2])
elif len(sys.argv) == 3 and sys.argv[1] == "-content":
    searchByContent(sys.argv[2])
elif len(sys.argv) == 5 and sys.argv[1] == '-type' and sys.argv[3] == '-name':
    searchDataByNameAndType(sys.argv[4], sys.argv[2])
elif len(sys.argv) == 5 and sys.argv[1] == '-name' and sys.argv[3] == '-type':
    searchDataByNameAndType(sys.argv[2], sys.argv[4])
"""
afficher_graphique()




