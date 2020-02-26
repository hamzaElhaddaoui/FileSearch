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

def searchDataByName(name, treeFrame):
    for i in treeFrame.get_children():
        treeFrame.delete(i)
    ix = open_dir("indexdir")

    # query_str is query string
    query_str = name+'*'
    print("Le nom a chercher ", name)
    # Top 'n' documents as result
    # topN = 3

    with ix.searcher(weighting=scoring.Frequency) as searcher:
        query = QueryParser("title", ix.schema).parse(query_str)
        results = searcher.search(query, terms=True, limit=None)
        if len(results) > 0:
            max = len(results)
            for i in range(max):
                treeFrame.insert("", "end", text="", values=(results[i]['title'], results[i]['path'], results[i]['extension'], results[i]['tags']))
                print("File Name: " + results[i]['title'], "Path: "+results[i]['path'], "Extension: " + results[0]['extension'])
        else:
            print("Aucun resultat trouvé !")

def searchDataByType(type, treeFrame):
    for i in treeFrame.get_children():
        treeFrame.delete(i)

    ix = open_dir("indexdir")

    query_str = type
    print('Le type a chercher ', type)
    with ix.searcher(weighting=scoring.Frequency) as searcher:
       query= QueryParser("extension", ix.schema).parse(query_str)
       results = searcher.search(query, terms=True, limit=None)
       if len(results) > 0:
           for i in range(len(results)):
               treeFrame.insert("", "end", text="", values=(results[i]['title'], results[i]['path'],results[i]['extension'],results[i]['tags']))
               print("File Name: " + results[i]['title'], "Path: " + results[i]['path'], "Contenu: "+results[i]['tags'],
                     "Extension: " + results[i]['extension'])
           print(results)
       else:
            print("Aucun resultat trouvé !")

def searchByContent(content, treeFrame):
    for i in treeFrame.get_children():
        treeFrame.delete(i)

    ix = open_dir("indexdir")

    query_str = content
    print('Le contenue a recherche est ', content)
    with ix.searcher(weighting=scoring.Frequency) as searcher:
        query = QueryParser("tags", ix.schema).parse(query_str)
        results = searcher.search(query, terms=True, limit=None)
        print(results)
        if len(results) > 0:
            for i in range(len(results)):
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


def chercher(input,type, treeFrame):
    if type == "Nom fichier":
        print(input.get())
        searchDataByName(input.get(), treeFrame)
    elif type == "Type fichier":
        searchDataByType(input.get(), treeFrame)
    elif type == "Contenu":
        searchByContent(input.get(), treeFrame)

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
    fenetre.minsize(900, 570)
    fenetre.resizable(0, 0)

    recherche = Frame(fenetre, width=500, height=200, borderwidth=2)
    recherche.pack()

    champ_label = Label(recherche, text="Entre le terme a chercher:", anchor="w", width=25, height=3)
    champ_label.grid(row=1, column=0)
    # champ_label.pack(side="top", fill=Y)
    var_text = StringVar()
    ligne_text = Entry(recherche, textvariable=var_text, width=60)
    print(var_text)
    ligne_text.grid(row=1, column=1)
    margeLabel=Label(recherche, width=10)
    margeLabel.grid(row=1, column=2)
    boutton_chercher = Button(recherche, text="Chercher", command=lambda: chercher(var_text, tkvar.get(), fileTable))
    boutton_chercher.grid(row=1, column=4)

    # Create a Tkinter variable
    tkvar = StringVar()
    # Dictionary with options
    choices = {'Nom fichier', 'Type fichier', 'Contenu'}
    tkvar.set('Nom fichier')
    popupMenu = OptionMenu(recherche, tkvar, *choices)  # set the default option
    popupMenu.grid(row=1, column=3)

    indexation = Frame(fenetre, width=500, height=200, borderwidth=2)
    indexation.pack()

    labelIndexation=Label(indexation, text="L'indexation :", anchor="w", width=20, height=3)
    labelIndexation.grid(row=1, column=0)

    labelPath=Label(indexation, text="", anchor="w", width=35, height=3)
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

    fileTable = ttk.Treeview(treeviewFrame, height=20)
    fileTable['columns'] = ("Nom fichier", "Path", "Extension", "Contenu")
    fileTable.grid(row=2, column=1, columnspan=5)
    fileTable.heading("#0", text="", anchor="w")
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
#elif sys.argv[1] == '-c':

 #   createSearchableData(root)

#elif len(sys.argv) == 3 and sys.argv[1] == '-name':
    #searchDataByName(sys.argv[2])

#elif len(sys.argv) == 3 and sys.argv[1] == '-type':
#    searchDataByType(sys.argv[2])
#elif len(sys.argv) == 3 and sys.argv[1] == '-content':
#    searchByContent(sys.argv[2])
# elif len(sys.argv) == 3 and sys.argv[1] == "-content":
#     searchByContent(sys.argv[2])

#elif len(sys.argv) == 5 and sys.argv[1] == '-type' and sys.argv[3] == '-name':
#    searchDataByNameAndType(sys.argv[4], sys.argv[2])
#elif len(sys.argv) == 5 and sys.argv[1] == '-name' and sys.argv[3] == '-type':
#    searchDataByNameAndType(sys.argv[2], sys.argv[4])

#fenetre.rowconfigure(0, weight=1)
#fenetre.columnconfigure(0, weight=1)
#typeDeRecherche = "nom"
afficher_graphique()




