import spacy
from offres_emploi import Api #pip install api-offres-emploi
from numpy import asarray

# Fonction si l'utilisateur souhaite faire une nouvelle recherche
def newRequest():
    while True:
        end = input("\n\nVoulez vous faire une nouvelle recherche ? [oui/non] ")
        if end in ["oui","non"] :
            return end
        else:
            print("Je n'ai pas compris, répondez par \"oui\" ou \"non\" ")

# Fonction pour récupéré la requete utilisateur
def request():
    entities = ["ORG","LOC","PER","MISC"]
    research = []
    ask = input("Souhaitez vous faire :\n1 - Une recherche classique.\n2 - Une recherche par entités.\n")
    while True:
        # Cas de recherche classique :
        if ask == "1":
            request = input("\nVeuillez entrer votre recherche : ")
            while True:
                for token in nlp(request):
                    # Dans le cas ou l'utilisateur ecrit une phrase, on ne récupère que les noms, les noms propres et les verbes (pour une recherche moins longue et plus précise)
                    if token.tag_ == "NOUN" or token.tag_ == "VERB" or token.tag_ == "PROPN":
                        research.append(token.text)
                if research != []:
                    print("\nRecherche en cours... \n")
                    return research, False
                else:
                    request = input("Je n'ai pas compris votre demande, veuillez réessayer : ")
        # Cas de recherche par entité : 
        elif ask == "2":
            nameEntitie = input("\nQuel est le nom de votre entité ? ")
            while True:
                # On verifie que les champs ne sont pas vide
                for token in nlp(nameEntitie):
                    research.append(token.text)
                if research != []:
                    typeEntitie = input("\nQuel est le type de cet entité :\nORG - compagnie, agence, institution.\nLOC - groupe géographique, pays, ville.\nPER - personnalité, nom de famille.\nMISC - autres (nationalités,produits,...)\n")            
                    while True:
                        if typeEntitie in entities:
                            research.append(typeEntitie)
                            print("\nRecherche en cours... \n")
                            return research, True
                        else:
                            typeEntitie = input("Valeur entrée incorrecte, veuillez réessayer : ")
                else:
                    nameEntitie = input("Je n'ai pas compris, quel est le nom de votre entité ? ")
        else:
            ask = input("Je n'ai pas compris votre demande, répondez par \"1\" ou \"2\".")

            
# Fonction pour trier/classer les annonces par ordre d'interet en fonction de leurs nombre d'apparition par requetes
def scoreSort(tab, tabScore):
    sort=[]
    dic = {}
    # tmpVal = Nombre d'apparition de l'annonce parmis toutes les requetes effectuer
    tmpVal = tab[0][1]
    z=0
    for x in range(len(tab)):
        z+=1
        # Si l'annonce précedente et l'anonce qu'on regarde sont apparu le meme nombre de fois, alors on met cette annonce dans un dictionnaire
        if tmpVal == tab[x][1]:
            # Clé = nom de l'annonce, Valeur = Score de similitude entre son libelle d'appellation et la requete de base
            dic[tab[x][0]] = tabScore[tab[x][0]]
        # Si les annonces ne sont pas apparus le meme nombre de fois : on trie le dictionnaire, on le vide dans un tableau "sort" et on met l'anonce actuel dedans.
        elif (tmpVal > tab[x][1]):
            
            dic = sorted(dic.items(), key=lambda t: t[1], reverse=True)
            for y in dic:
                sort.append(y[0])
            dic={}
            tmpVal = tab[x][1]
            dic[tab[x][0]] = tabScore[tab[x][0]]
    # Une fois qu'on a parcouru toute les annonces, on trie le dictionnaire et on le vide dans le tableau "sort"
    dic = sorted(dic.items(), key=lambda t: t[1], reverse=True)
    for y in dic:
        sort.append(y[0])
    # On retourne le tableau "sort" qui contient touts les intitulés d'annonce dans le bon ordre d'interet.
    # Les premières annonces seront celle avec le nombre d'apparition la plus élevé.
    # Si plusieurs annonces ont un nombre égale : Les premières parmis elles seront celle qui seront le plus proche avec la requete utilisateur
    return sort


# Menu pour afficher le détail des offres
def detailsOffer(index): 
    while True:

        if index == "stop":
            return False
        
        elif index == "":
            return True

        else:
            print("\nIntitule :",searchResult[search[int(index)-1]]["intitule"],"\n\nDescription :",searchResult[search[int(index)-1]]["description"],"\n\nLieu :",searchResult[search[int(index)-1]]["lieuTravail"]["libelle"],"\n\nType de contrat :",searchResult[search[int(index)-1]]["typeContrat"])
            if "libelle" in searchResult[search[int(index)-1]]["salaire"]:   
                print("\nSalaire :",searchResult[search[int(index)-1]]["salaire"]["libelle"],"\n\nHoraire de travail :",searchResult[search[int(index)-1]]["dureeTravailLibelle"],"\n\nVous pouvez retouver l'offre à cette adresse :",searchResult[search[int(index)-1]]["origineOffre"]["urlOrigine"])
            else:
                print("\nSalaire :","Non communiqué","\n\nHoraire de travail :",searchResult[search[int(index)-1]]["dureeTravailLibelle"],"\n\nVous pouvez retouver l'offre à cette adresse :",searchResult[search[int(index)-1]]["origineOffre"]["urlOrigine"])                        

        index = input("\n\nTapez le numéro d'une offre pour plus de détail. Si vous voulez continuer, tapez sur entrée. Si vous voulez arreter, tapez stop : ")

            


print("Bonjour a vous,\n\nBienvenue dans ce moteur de recherche de contrat de travail, merci de patienter un instant...\n")

nlp = spacy.load("fr_core_news_lg")
client = Api(client_id="PAR_toccupes_cd7d5ac5354e7e76ae1a52a04d9c61d9eb6503b5177b91efdb131e6315fbaa07",
             client_secret="e517f83dae8f2a814409e64d3afadf3456317ae15554c9f356c45b56c0cf145d")

while True:
    tab=[]
    search = {}
    searchResult = {}
    searchScore = {}

    # Requete utilisateur : Recherche classique par mots clés -> recherche seulement sur les noms et les verbes
                          # Recherche par entités -> recherche sur les mots similaires au nom de l'entité

    research, entitie = request()

    if entitie :
        typeEntitie = research[1]
        nameEntitie = research[0]
        research = [nameEntitie]
        nameEntitie2 = nameEntitie.lower()
        research.append(nameEntitie2)
        
    # Récuperer les mots similaires a la requete utilisateur
    keyss,_,scoress = nlp.vocab.vectors.most_similar(asarray([nlp(word).vector for word in research]),n=100)
    for keys, scores in zip(keyss, scoress):
        strings = [nlp.vocab.strings[key] for key in keys]
        for string, score in zip(strings,scores):
            if score > 0.65:
                tab.append(string)


    doc1 = nlp(research[0])
    
    for keyWord in tab: # Recherche sur l'api pour chaque mots similaire à la requete utilisateur

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
            
            for i in my_search["resultats"]:    # trier les résultats par leurs nombre d'apparition dans par requete
                doc2 = nlp(my_search['resultats'][x]['appellationlibelle']) 
                if (my_search['resultats'][x]["intitule"] in search.keys()) and (my_search['resultats'][x]["description"] == searchResult[my_search['resultats'][x]["intitule"]]["description"]):
                    search[my_search['resultats'][x]["intitule"]] += 1
                    if doc2.has_vector:
                        searchScore[my_search['resultats'][x]["intitule"]] = doc1.similarity(doc2)
                    else:
                        searchScore[my_search['resultats'][x]["intitule"]] = 0.00
                 
                elif (my_search['resultats'][x]["intitule"] in search.keys()) and (my_search['resultats'][x]["description"] != searchResult[my_search['resultats'][x]["intitule"]]["description"]):

                    search["("+str(y)+")"+str(my_search['resultats'][x]["intitule"])] = 1
                    searchResult["("+str(y)+")"+str(my_search['resultats'][x]["intitule"])] = my_search['resultats'][x]

                    if doc2.has_vector:
                        searchScore["("+str(y)+")"+str(my_search['resultats'][x]["intitule"])] = doc1.similarity(doc2)
                    else:
                        searchScore["("+str(y)+")"+str(my_search['resultats'][x]["intitule"])] = 0.00    

                    if entitie:   # trier les résultats par leurs nombre d'apparition par requete + le nombre d'apparition de l'entité nommés
                        doc = nlp(my_search["resultats"][x]["description"])
                        for token in doc.ents:
                            if (token.text == nameEntitie or token.text == nameEntitie2) and token.label_ == typeEntitie:
                                search["("+str(y)+")"+str(my_search['resultats'][x]["intitule"])] += 1
                    y+=1          

                else :
                    
                    search[my_search['resultats'][x]["intitule"]] = 1
                    searchResult[my_search['resultats'][x]["intitule"]] = my_search['resultats'][x]
                    
                    if doc2.has_vector:
                        searchScore[my_search['resultats'][x]["intitule"]] = doc1.similarity(doc2)
                    else:
                        searchScore[my_search['resultats'][x]["intitule"]] = 0.00
                        
                    if entitie: 
                        doc = nlp(my_search["resultats"][x]["description"])
                        for token in doc.ents:
                            if (token.text == nameEntitie or token.text == nameEntitie2) and token.label_ == typeEntitie:
                                search[my_search['resultats'][x]["intitule"]] += 1 
                        
                x+=1
    search = sorted(search.items(), key=lambda t: t[1], reverse=True)   
    search = scoreSort(search, searchScore) # trier les doublons de nombre de requete par leurs similarité décroissante entre leurs "appelationlibelle" et la requete utilisateur

    y=0
    print(len(search),"offres trouvés : \n")
    for x in search:
        y+=1
        print("[",str(y),"] -",x)
        if(not y%10):
            detail = input("\n\nTapez le numéro d'une offre pour plus de détail. Si vous voulez continuer, tapez sur entrée. Si vous voulez arreter, tapez stop : ")
            if not detailsOffer(detail):
                break
            print("")
            
        
    if newRequest() == "non":
        print("\nMerci d'avoir utilisé notre outil !")
        break

