import spacy
from offres_emploi import Api
import numpy
from numpy import asarray



def finRequete():
    stop = False
    yes = ["oui","Oui","OUI","o","O"]
    no = ["non","Non","NON","n","N"]
    while not stop:
        fin = input("\ncontinuer la recherche ? [oui/non]")
        if fin in yes:
            print("Lancement.....................................\n")
            return False
        elif fin in no:
            print("Fin des recherches.................................")
            return True
        else:
            print("Je n'ai pas compris, répondez par \"oui\" ou \"non\" ")



def scoreSort(tab, tabScore):
    sort=[]
    dic = {}
    tmpVal = tab[0][1]
    z=0
    for x in range(len(tab)):
        z+=1
        if tmpVal == tab[x][1]:
            dic[tab[x][0]] = tabScore[tab[x][0]]
        elif (tmpVal > tab[x][1]):
            dic = sorted(dic.items(), key=lambda t: t[1], reverse=True)
            for y in dic:
                sort.append(y[0])
            dic={}
            tmpVal = tab[x][1]
            dic[tab[x][0]] = tabScore[tab[x][0]]
    dic = sorted(dic.items(), key=lambda t: t[1], reverse=True)
    for y in dic:
        sort.append(y[0])
    return sort
            
                
            


print("Bonjour a vous,\n\nBienvenue dans ce moteur de recherche de contrat de travail\n")

nlp = spacy.load("fr_core_news_lg")
client = Api(client_id="PAR_toccupes_cd7d5ac5354e7e76ae1a52a04d9c61d9eb6503b5177b91efdb131e6315fbaa07",
             client_secret="e517f83dae8f2a814409e64d3afadf3456317ae15554c9f356c45b56c0cf145d")




while True:
    recherche = []
    tab=[]
    search = {}
    searchResult = {}
    searchScore = {}

    # Requete utilisateur prenant en compte seulement les noms de la recherche
    request = input("Veuillez entrer votre recherche : ")
    for token in nlp(request):
        if token.tag_ == "NOUN":
            recherche.append(str(token.text))
    print("")
    
    # Récuperer les mots similaires a la requete utilisateur
    keyss,_,scoress = nlp.vocab.vectors.most_similar(asarray([nlp(word).vector for word in recherche]),n=100)
    for keys, scores in zip(keyss, scoress):
        strings = [nlp.vocab.strings[key] for key in keys]
        for string, score in zip(strings,scores):
            if score > 0.65:
                tab.append(string)

    doc1 = nlp(recherche[0])
    
    for motCle in tab: # Recherche sur l'api pour chaque mots similaire a la requete utilisateur
        
        arg={
            "motsCles":motCle,
            "range":"0-20"
            }
        my_search = client.search(params=arg)
        y=0
        for x in range(len(my_search["resultats"])):    # trier les résultats par leurs nombre d'apparition dans chaque requetes 
            doc2 = nlp(my_search['resultats'][x]['appellationlibelle']) 
            if (my_search['resultats'][x]["intitule"] in search.keys()) and (my_search['resultats'][x]["description"] == searchResult[my_search['resultats'][x]["intitule"]]["description"]):
                search[my_search['resultats'][x]["intitule"]] += 1
                searchScore[my_search['resultats'][x]["intitule"]] = doc1.similarity(doc2)
            elif (my_search['resultats'][x]["intitule"] in search.keys()) and (my_search['resultats'][x]["description"] != searchResult[my_search['resultats'][x]["intitule"]]["description"]):
                search["("+str(y)+")"+str(my_search['resultats'][x]["intitule"])] = 1
                searchScore["("+str(y)+")"+str(my_search['resultats'][x]["intitule"])] = doc1.similarity(doc2)
                searchResult["("+str(y)+")"+str(my_search['resultats'][x]["intitule"])] = my_search['resultats'][x]
                y+=1
            else :
                search[my_search['resultats'][x]["intitule"]] = 1
                searchScore[my_search['resultats'][x]["intitule"]] = doc1.similarity(doc2)
                searchResult[my_search['resultats'][x]["intitule"]] = my_search['resultats'][x]

    search = sorted(search.items(), key=lambda t: t[1], reverse=True)
   
    search = scoreSort(search, searchScore) # trier les doublons de nombre de requete par leurs similarité décroissante
                                            # entre leurs appelationlibelle et la requete utilisateur

    # Affichage des resultats de la recherches
    y=0
    for x in search:
        y+=1
        print("[",str(y),"] -",x)
        


    
    if finRequete():
        break



#Pour récupéré les entitées nommées : 
#for token in doc.ents:
#    print(token.text,token.label_)


# Pour trier les mots de la recherche ? (pas de determinant ou de verbe par exemple)
##doc = nlp("je travaille en tant que boulanger")
##for token in doc:
##    if token.tag_ == "NOUN":
##        print(token.text)



