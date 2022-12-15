import spacy
from offres_emploi import Api #pip install api-offres-emploi
import numpy
from numpy import asarray


def newRequete():
    while True:
        end = input("\n\nVoulez vous faire une nouvelle recherche ? [oui/non] ")
        if end in ["oui","non"] :
            return end
        else:
            print("Je n'ai pas compris, répondez par \"oui\" ou \"non\" ")


def request():
    research = []
    request = input("Veuillez entrer votre recherche : ")
    while True:
        for token in nlp(request):
            if token.tag_ == "NOUN" or token.tag_ == "VERB":
                research.append(token.text)
        if research != []:
            print("\nRecherche en cours... \n")
            return research
        else:
            request = input("Je n'ai pas compris votre demande, veuillez réessayer : ")

            
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

            
def detailsOffer(index):
    while True:
        if index == "":
            break
        else:
            print("\nIntitule :",searchResult[search[int(index)-1]]["intitule"],"\n\nDescription :",searchResult[search[int(index)-1]]["description"],"\n\nLieu :",searchResult[search[int(index)-1]]["lieuTravail"]["libelle"],"\n\nType de contrat :",searchResult[search[int(index)-1]]["typeContrat"])
            if "libelle" in searchResult[search[int(index)-1]]["salaire"]:   
                print("\nSalaire :",searchResult[search[int(index)-1]]["salaire"]["libelle"],"\n\nHoraire de travail :",searchResult[search[int(index)-1]]["dureeTravailLibelle"],"\n\nVous pouvez retouver l'offre à cette adresse :",searchResult[search[int(index)-1]]["origineOffre"]["urlOrigine"])
            else:
                print("\nSalaire :","Non communiqué","\n\nHoraire de travail :",searchResult[search[int(index)-1]]["dureeTravailLibelle"],"\n\nVous pouvez retouver l'offre à cette adresse :",searchResult[search[int(index)-1]]["origineOffre"]["urlOrigine"])                        

        index = input("\n\nTapez le numéro d'une offre pour plus de détail. Si vous voulez continuer, tappez sur entrée : ")

            


print("Bonjour a vous,\n\nBienvenue dans ce moteur de recherche de contrat de travail, merci de patienter un instant...\n")

nlp = spacy.load("fr_core_news_lg")
client = Api(client_id="PAR_toccupes_cd7d5ac5354e7e76ae1a52a04d9c61d9eb6503b5177b91efdb131e6315fbaa07",
             client_secret="e517f83dae8f2a814409e64d3afadf3456317ae15554c9f356c45b56c0cf145d")


while True:
    tab=[]
    search = {}
    searchResult = {}
    searchScore = {}
    research = request()

    # Récuperer les mots similaires a la requete utilisateur
    keyss,_,scoress = nlp.vocab.vectors.most_similar(asarray([nlp(word).vector for word in research]),n=100)
    for keys, scores in zip(keyss, scoress):
        strings = [nlp.vocab.strings[key] for key in keys]
        for string, score in zip(strings,scores):
            if score > 0.65:
                tab.append(string)

    doc1 = nlp([0])
    
    for keyWord in tab: # Recherche sur l'api pour chaque mots similaire a la requete utilisateur
        hasResult = True
        arg={
            "motsCles":keyWord,
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
   
    search = scoreSort(search, searchScore) # trier les doublons de nombre de requete par leurs similarité décroissante
                                            # entre leurs appelationlibelle et la requete utilisateur
    y=0
    for x in search:
        y+=1
        print("[",str(y),"] -",x)
        if(not y%10):
            detail = input("\n\nTapez le numéro d'une offre pour plus de détail. Si vous voulez continuer, tappez sur entrée : ")
            detailsOffer(detail);
            print("")

    if(not y%10):
        detail = input("\n\nIl n'y a plus d'autres offres. Tapez le numéro d'une offre pour plus de détail. Si vous voulez continuer, tappez sur entrée : ")

                    
        
    if newRequest() == "non":
        print("Merci d'avoir utilisé notre outils!")
        break

#Pour récupéré les entitées nommées : 
#for token in doc.ents:
#    print(token.text,token.label_)


# Pour trier les mots de la recherche ? (pas de determinant ou de verbe par exemple)
##doc = nlp("je travaille en tant que boulanger")
##for token in doc:
##    if token.tag_ == "NOUN":
##        print(token.text)



