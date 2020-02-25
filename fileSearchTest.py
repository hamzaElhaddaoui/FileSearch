import os
import sys
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser
from whoosh import scoring
from whoosh.index import open_dir
from whoosh import qparser
from tkinter import *
from tkinter import ttk
from threading import *
from threading import RLock
from tkinter import filedialog

def addInIndex(writer,root):
    nbIndexed=0
    print("---------------------------------------------")
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
        for name in dirs:
            print("*****************************")
            print(os.path.join(root, name))
    print("---------------------------------------------")
    print(nbIndexed)

verrou = RLock()

def createSearchableData(root):
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
        addInIndex(writer, root)
        writer.commit()
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
               treeFrame.insert("", "end", text="", values=(results[i]['title'],results[i]['path'],results[i]['extension'],results[i]['tags']))
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
    def __init__(self, root, bottonUpdate, bottonChercher):
        Thread.__init__(self)
        self.path = root
        self.bottonUpdate = bottonUpdate
        self.bottonChercher = bottonChercher
    def run(self):
        self.bottonUpdate["state"] = "disabled"
        self.bottonChercher["state"] = "disabled"
        createSearchableData(self.path)
        self.bottonUpdate["state"] = "normal"
        self.bottonChercher["state"] = "normal"

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
    boutton_chercher = Button(recherche, text="Chercher", command=lambda: chercher(var_text, tkvar.get(), EmployView))
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

    labelIndexation=Label(indexation, text="L'indexation :", anchor="w", width=25, height=3)
    labelIndexation.grid(row=1, column=0)

    labelPath=Label(indexation, text="", anchor="w", width=60, height=3)
    labelPath.grid(row=1, column=1)
    labelPath['text'] = root

    button_updateDb = Button(indexation, text="Update BD", command=lambda: GenererBD(labelPath['text'], button_updateDb, boutton_chercher).start(), width=17)
    button_updateDb.grid(row=1, column=5)
    button_updateDb['state'] = "disabled"

    button2 = Button(indexation, text="Browse", command=lambda: browse_button(button_updateDb, labelPath))
    button2.grid(row=1, column=4)

    # link function to change dropdown
    #tkvar.trace('w', change_dropdown)
    treeviewFrame = Frame(fenetre)
    treeviewFrame.pack()

    EmployView = ttk.Treeview(treeviewFrame, height=20)
    EmployView['columns'] = ("Nom fichier", "Path", "Extension", "Contenu")
    EmployView.grid(row=2, column=1, columnspan=5)
    EmployView.heading("#0", text="", anchor="w")
    EmployView.column("#0", anchor="center", width=5, stretch=NO)
    EmployView.heading("Nom fichier", text="Nom fichier", anchor="w")
    EmployView.column("Nom fichier", anchor="w", width=240)
    EmployView.heading("Path", text="Path", anchor="w")
    EmployView.column("Path", anchor="w", width=240)
    EmployView.heading("Extension", text="Extension", anchor="w")
    EmployView.column("Extension", anchor="w", width=90)
    EmployView.heading("Contenu", text="Contenu", anchor="w")
    EmployView.column("Contenu", anchor="w", width=240)
    EmployViewScrollbar = ttk.Scrollbar(treeviewFrame, orient="vertical", command=EmployView.yview)
    EmployView.configure(yscroll=EmployViewScrollbar.set)
    EmployViewScrollbar.grid(row=2, column=6, sticky="ns")

    EmployView.insert("", "end", text="", values=("hamza", "toto", "tantan", "rae"))
    fenetre.mainloop()

root = "F:\\Programme"
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




