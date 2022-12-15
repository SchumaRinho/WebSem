import spacy
from offres_emploi import Api #pip install api-offres-emploi
import numpy
from numpy import asarray



def finRequete():
    stop = False
    yes = ["oui","Oui","OUI","o","O"]
    no = ["non","Non","NON","n","N"]
    while not stop:
        fin = input("\ncontinuer la recherche ? [oui/non]")
        if fin in yes:
            print("\nLancement..........................................\n")
            return False
        elif fin in no:
            print("\nFin des recherches.................................")
            return True
        else:
            print("Je n'ai pas compris, répondez par \"oui\" ou \"non\" ")


def requete():
    recherche = []
    ask = input("Souhaitez vous faire :\n1 - Une recherche classique.\n2 - Une recherche par entités.")
    while True:
        if ask == 1:
            request = input("\nVeuillez entrer votre recherche : ")
            while True:
                for token in nlp(request):
                    if token.tag_ == "NOUN" or token.tag_ == "VERB":
                        recherche.append(token.text)
                if recherche != []:
                    print("\nRecherche en cours... \n")
                    return recherche
                else:
                    request = input("Je n'ai pas compris votre demande, veuillez réessayer : ")
        elif ask == 2:
            nomEntite = input("\nQuel est le nom de votre entité ? ")
            typeEntite = input("Quel est le type de cet entité :\nORG - une compagnie, une agence, une institution.\nGPE - Un groupe géopolitique, un pays, une ville.\nPERSON - une personnalité connu.\nPRODUCT - un produit connu.")            
        else:
            ask = input("Je n'ai pas compris votre demande, répondez par \"1\" ou \"2\".")

            
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
    dic = sorted(dic.items(), key=lambda t: t[1], reverse=True)
    for y in dic:
        sort.append(y[0])
    return sort
            
                
            


print("Bonjour a vous,\n\nBienvenue dans ce moteur de recherche de contrat de travail, merci de patienter un instant...\n")

nlp = spacy.load("fr_core_news_lg")
client = Api(client_id="PAR_toccupes_cd7d5ac5354e7e76ae1a52a04d9c61d9eb6503b5177b91efdb131e6315fbaa07",
             client_secret="e517f83dae8f2a814409e64d3afadf3456317ae15554c9f356c45b56c0cf145d")


stop = False



while not stop:
    tab=[]
    search = {}
    searchResult = {}
    searchScore = {}

    # Requete utilisateur : Recherche effectuer seulement sur les noms et les verbes
    recherche = requete()
    
    # Récuperer les mots similaires a la requete utilisateur
    keyss,_,scoress = nlp.vocab.vectors.most_similar(asarray([nlp(word).vector for word in recherche]),n=100)
    for keys, scores in zip(keyss, scoress):
        strings = [nlp.vocab.strings[key] for key in keys]
        for string, score in zip(strings,scores):
            if score > 0.65:
                tab.append(string)

    doc1 = nlp(recherche[0])
    
    for motCle in tab: # Recherche sur l'api pour chaque mots similaire a la requete utilisateur
        hasResult = True
        arg={
            "motsCles":motCle,
            "range":"0-20"
            }
        try:
            my_search = client.search(params=arg)
        except AttributeError:
            hasResult = False
        if hasResult:
            x=0
            y=0
            for i in my_search["resultats"]:    # trier les résultats par leurs nombre d'apparition dans chaque requetes 
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
                x+=1
    search = sorted(search.items(), key=lambda t: t[1], reverse=True)
    y=0
   
    search = scoreSort(search, searchScore) # trier les doublons de nombre de requete par leurs similarité décroissante
                                            # entre leurs appelationlibelle et la requete utilisateur

    y=0
    for x in search:
        y+=1
        print("[",str(y),"] -",x)
        if(not y%10):
            detail = input("\nTapez le numéro de l'offre pour plus de détail. Si vous voulez continuer, tappez sur entrée : ")
            while True:
                if detail == "":
                    break
                else:
                    print("\nIntitule :",searchResult[search[int(detail)-1]]["intitule"],"\n\nDescription :",searchResult[search[int(detail)-1]]["description"],"\n\nLieu :",searchResult[search[int(detail)-1]]["lieuTravail"]["libelle"],"\n\nType de contrat : ",searchResult[search[int(detail)-1]]["typeContrat"])

                detail = input("\nTapez le numéro de l'offre pour plus de détail. Si vous voulez continuer, tappez sur entrée : ")

        

    stop = finRequete()



#Pour récupéré les entitées nommées : 
#for token in doc.ents:
#    print(token.text,token.label_)



