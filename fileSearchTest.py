import os
import sys
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser
from whoosh import scoring
from whoosh.index import open_dir
from whoosh import qparser

def addInIndex(writer,root):
    nbIndexed=0
    print("---------------------------------------------")
    for root, dirs, files in os.walk(root, topdown=True):
        for name in files:
            path = os.path.join(root, name)
            extension = name.split(".")[len(name.split(".")) - 1]
            print(path)
            print(name)
            print(extension)
            # fp = open(path, 'r')
            # if fp.mode == 'r' and extension == "txt":
            #     print("--------------file is opened")
            #     text = fp.read()
            #     print(text)
            #     print("------------------------")
            # else:
            #     text = "Incompatible content"
            # fp.close()
            nbIndexed += 1
            text = "toto"
            writer.add_document(title=name, path=path, content=text, tags=text, extension=extension)
        for name in dirs:
            print("*****************************")
            print(os.path.join(root, name))
    print("---------------------------------------------")
    print(nbIndexed)

def createSearchableData(root):
    '''
    Schema definition: title(name of file), path(as ID), content(indexed
    but not stored),textdata (stored text content)
    '''
    schema = Schema(title=TEXT(stored=True), path=ID(stored=True), content=TEXT, tags=TEXT(stored=True), extension=TEXT(stored=True))

    if not os.path.exists("indexdir"):
        os.mkdir("indexdir")

    # Creating a index writer to add document as per schema
    ix = create_in("indexdir", schema)

    writer = ix.writer()
    addInIndex(writer, root)
    writer.commit()

def searchDataByName(name):
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
                print("File Name: " + results[i]['title'], "Path: "+results[i]['path'], "Tags: " + results[i]['tags'], "Extension: " + results[0]['extension'])
        else:
            print("Aucun resultat trouvé !")

def searchDataByType(type):
   ix = open_dir("indexdir")

   #setup the query
   query_str = type
   print('Le type a chercher ', type)
   with ix.searcher(weighting=scoring.Frequency) as searcher:
       query= QueryParser("extension", ix.schema).parse(query_str)
       results = searcher.search(query, terms=True, limit=None)
       if len(results) > 0:
           for i in range(len(results)):
               print("File Name: " + results[i]['title'], "Path: " + results[i]['path'], "Tags: " + results[i]['tags'],
                     "Extension: " + results[0]['extension'])
           print(results)
       else:
            print("Aucun resultat trouvé !")

def searchByContent(content):
    ix = open_dir("indexdir")

    query_str = '*'+content+'*'
    print('Le contenue a recherche est ', content)
    with ix.searcher(weighting=scoring.Frequency) as searcher:
        query = QueryParser("tags", ix.schema).parse(query_str)
        results = searcher.search(query, terms=True, limit=None)
        if len(results) > 0 :
            for i in range(len(results)):
                print("File Name: " + results[i]['title'], "Path: " + results[i]['path'], "Tags: " + results[i]['tags'],
                     "Extension: " + results[0]['extension'])
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
                print("File Name: " + results[i]['title'], "Path: " + results[i]['path'], "Tags: " + results[i]['tags'],
                      "Extension: " + results[0]['extension'])
                print(results)
        else:
            print("Aucun resultat trouvé !")

root = "F:\\Programme"
# createSearchableData(root)
# searchData()
if len(sys.argv) < 2 or len(sys.argv) > 5:

    print("Please use proper format")
    print("Use < fileSearchTest -c > to create database file")
    print("Use < fileSearchTest -name name_file > to search file")
    print("Use < fileSearchTest -type extension > to search by extension")
    # print("Use < fileSearchTest -content term_to_search > to search by content")
    print(len(sys.argv))
    print(sys.argv[1])
    print(sys.argv[3])
elif sys.argv[1] == '-c':

    createSearchableData(root)

elif len(sys.argv) == 3 and sys.argv[1] == '-name':
    searchDataByName(sys.argv[2])

elif len(sys.argv) == 3 and sys.argv[1] == '-type':
    searchDataByType(sys.argv[2])

# elif len(sys.argv) == 3 and sys.argv[1] == "-content":
#     searchByContent(sys.argv[2])

elif len(sys.argv) == 5 and sys.argv[1] == '-type' and sys.argv[3] == '-name':
    searchDataByNameAndType(sys.argv[4], sys.argv[2])
elif len(sys.argv) == 5 and sys.argv[1] == '-name' and sys.argv[3] == '-type':
    searchDataByNameAndType(sys.argv[2], sys.argv[4])