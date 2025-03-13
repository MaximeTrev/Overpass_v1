import streamlit as st
import pandas as pd
import json
import time
import unidecode as u
import os

from requetes import Requetes as R

def __suppr__(chain, Liste) : #sous-fonction
    ch = chain.upper()
    occ, i = Liste[0], 1
    lengthListe = len(Liste)
    while occ not in ch and i<lengthListe:
        occ = Liste[i]
        i+=1
    if i==lengthListe :
        return chain
    ch = ch.replace(occ, "")
    return ch.capitalize()

ListeLabel = [" SE", " SARL", " EI", " EURL", " SASU", " SAS", " SA", " SNC", " SCS", " SCA"]

def fromJSONtoDataFrame(Fichiers) : #Fichiers une liste de fichiers (JSON)
    Name = []
    Flag = []
    Lat = []
    Lon = []
    Source = []
    Amenity, Place, Shop, Power, Highway = [],[],[],[],[]
    for i in range(len(Fichiers)) :
        
        booleen = True
        
        if ".json" not in Fichiers[i] :
            booleen = False
        else:
            try:
                with open("json/"+Fichiers[i], "r") as JSON:
                    j = 1
                    dico = json.load(JSON)
                    for occ in dico :
                        dic = dico["iteration "+str(j)]
                        
                        try: Amenity.append(dic["amenity"]) 
                        #si amenity n'est pas renseigné cela renvoie une exception / erreur
                        #on va donc l' "attraper" avec Except et lui définir une valeur pré-choisie
                        except: Amenity.append("X")
                        
                        try: Source.append(dic["source"])
                        except: Source.append("X")
                        
                        try: Place.append(dic["place"])
                        except: Place.append("X")
                        
                        try: Shop.append(dic["shop"])
                        except: Shop.append("X")
                        
                        try: Power.append(dic["power"])
                        except: Power.append("X")
                        
                        try: Highway.append(dic["highway"])
                        except: Highway.append("X")
                        
                        Name.append(dic["name"])
                        Coordonnees = dic["coord"].split("/")
                        Lat.append(Coordonnees[0])
                        Lon.append(Coordonnees[1])
                        Flag.append(dic["flag"])
                        j+=1
                        booleen = True
            except:
                print(Fichiers[i], "fichier vide.")
                    
    if booleen :
        data = {"Source": Source, "Name": Name, "Amenity": Amenity, "Place": Place, "Shop": Shop, "Power": Power, "Highway": Highway, "Lat": Lat, "Long": Lon, "Flag": Flag}
        df = pd.DataFrame(data)
   
        print("\n",booleen, ": File saved.")
        return df
    else:
        print("\n",booleen, ": aucun fichier JSON trouvé.")

def __var_name__(name, booleen = False): #sous-fonction
    out = [] # 0 --> nom initial et on boucle direct dessus ?
    out.append((name))
    out.append((name.upper()))
    out.append((name.lower()))
    out.append((name.capitalize()))
    tests = [" ", "-","_"]
    test_esp = False
    
    
    for test in tests:
        #BLoc pour vérifier si 2 mots (ou plus) dans la chaîne
        #marche pas si plusieurs "sépérateurs" pour une chaîne
        if test in name:
            #bloc pour le test "mots composés"
            test_esp = test
            #ICI bloc pour le test "classique"
            #espace = test
            tests.remove(test)
            break
        
    for espace in tests:
        if test_esp :
            newName = name.replace(test_esp, espace)
            out.append((newName.upper()))
            out.append((newName.lower()))
            out.append((newName.capitalize()))
    
    out = set(out) #supprime automatiquement les éventuels doublons
    liste = []
    
    i = 1
    for val in out :
        
        if val == name and not booleen :
            (val, index) = (name, 0) #flag initial
            val = (val, index)
        else :
            val = (val, i)
        liste.append(val)
        i += 1
    return liste # --> set avec toutes les variations de noms

##########################################################################################################################

def fromCSVtoJSON(option, progress_container, NomEntreprise="", FichierCSV="", i=1) :
    
    """
    - Paramètres
    --------------------------------------------------------------
    fichierCSV : TYPE
        Fichier CSV
        Format fichier CSV :
            - Nom de l'entreprise
            - Nom de l'entreprise à concaténer au nom du fichier en sortie
            - Requête (Overpass turbo)
            - délimiteur : | (sans espaces)
    
    - Tâche
    --------------------------------------------------------------
    Crée un fichier JSON pour 
    chaque entreprise.
    """
    
    print("Options :s \n 1 - Générer un fichier CSV depuis un autre fichier CSV. \n 2 - Générer un fichier CSV depuis une seule entreprise. \n")
    
    entreprises = []
    if not os.path.exists("json"):
        os.makedirs("json")
        
    if FichierCSV != "":
        FichierCSV.seek(0)  # Revenir au début du fichier

        # Lire le fichier en ignorant le BOM UTF-8
        file_content = FichierCSV.getvalue().decode("utf-8-sig")
    
        # Diviser en lignes sans supprimer les espaces
        lines = file_content.split("\r\n")
    
        # Vérifier qu'on a bien un en-tête et des données
        if len(lines) > 1:
            spamreader = pd.DataFrame({lines[0]: lines[1:]})  # Première ligne devient le nom de colonne
            entreprises = lines[1:]
        else:
            st.error("Le fichier ne contient pas assez de données exploitables.")
        #"csv/datas2.csv"
        listeFichiers = []
        temps = 0.0
        compteurRequetes, compteurBatiments = 0, 0
        j=0
        max_length = len(list(spamreader.iterrows()))-1  #enlever la ligne du nom de colonne(s)
        
        for occ, row in spamreader.iterrows():
            
            i=1
            j+=1
            fName = row.iloc[0]
            fname = __suppr__(fName, ListeLabel)
            fName = fname
            
            
            varName, varName_ = [], []
            varName = __var_name__(fName) #avec accents
            #print("varName :", varName)
            
            fName_ = u.unidecode(fName)
            if fName_ != fName :
                varName_ = __var_name__(fName_, True) #True -> pas d'accent, donc le nom initial n'est pas présent
                #print("varName_ :",varName_)
    
            IndNomInitial = varName.index((fName, 0))
            (nomInitial, _) = varName[IndNomInitial]
 
            time.sleep(1)
            res = {}
            try:
                with open("json/"+fName+".json", "w", encoding="utf-8") as f1:
                    for (var, flag) in varName :
                        
                        # --------------
                        
                        #req = 'node [name='+'"'+var+'"];out;'
                        #possiblement faire 3 requetes: node, way, relation et extraire separement node way etc plutot que juste les nodes
                        #req = 'nwr [name='+'"'+var+'"];(._;>;);out;'
                        req = """node[name='+'"'+var+'"];
                              way[name='+'"'+var+'"];
                              relation[name='+'"'+var+'"];
                             ;
                            out center;"""
                        
                        compteurRequetes += 1
                        requete = R.safe_query(req)
                        res, i, batiments = R.requestToDict(requete, flag, nomInitial, res, i)
                        compteurBatiments += batiments
                        
                    time.sleep(1)    
                    for (var, flag) in varName_ :
                        
                        # --------------
                        
                        #req ='node [name='+'"'+var+'"];out;'
                        #req = 'nwr [name='+'"'+var+'"];(._;>;);out;'
                        req = """node[name='+'"'+var+'"];
                              way[name='+'"'+var+'"];
                              relation[name='+'"'+var+'"];
                             ;
                            out center;"""
                        compteurRequetes += 1
                        requete = R.safe_query(req)
                        print(requete)
                        res, i, batiments = R.requestToDict(requete, flag, nomInitial, res, i)
                        compteurBatiments += batiments
                    if res != {} :
                        json.dump(res, f1)
                        listeFichiers.append(fName+".json")
                progress=j/max_length*100
                progress=round(progress)
                progress_container.markdown(
                    f"""<div class="progress-bar" style="width: {progress}%;">
                    {progress}%
                </div>""",
                    unsafe_allow_html=True
                )
            except:
                print(fName, ": On ne peut pas créer le fichier.")
            print("Nombre de requêtes exécutées :",compteurRequetes)            
            print("Nombre de bâtiments trouvés :",compteurBatiments)
        
        print("Temps de génération fichier/s :", str(round(temps-2))+" secondes.\n") #-2 car on a fait time.sleep(1)*2
        print(listeFichiers)
        return listeFichiers, entreprises
    
    elif NomEntreprise != "" :
        listeFichiers = []
        
        fname = __suppr__(NomEntreprise, ListeLabel) 
        print("Name :", fname)
        fName = fname
        
        temps = 0.0
        compteurRequetes, compteurBatiments = 0, 0
        
        varName, varName_ = [], []
        varName = __var_name__(fName) #avec accents
        #print("varName :", varName)
        
        fName_ = u.unidecode(fName)
        if fName_ != fName :
            varName_ = __var_name__(fName_, True) #True -> pas d'accent, donc le nom initial n'est pas présent
            #print("varName_ :",varName_)

        IndNomInitial = varName.index((fName, 0))
        (nomInitial, _) = varName[IndNomInitial]
 
        time.sleep(1)
        res = {}
        max_length=len(varName)+len(varName_)
        j=0
        with open("json/"+fName+".json", "w", encoding="utf-8") as f1:
            for (var, flag) in varName :
                j+=1
                
                # --------------
                
                #req = 'node [name='+'"'+var+'"];out;'
                #req = 'nwr [name='+'"'+var+'"];(._;>;);out;'
                req = f"""(node[name='{var}'];
                              way[name='{var}'];
                              relation[name='{var}'];
                             );
                            """
                compteurRequetes += 1
                requete = R.safe_query(req)
                res, i, batiments = R.requestToDict(requete, flag, nomInitial, res, i)
                compteurBatiments += batiments
                
                progress=j/max_length*100
                progress=round(progress)
                progress_container.markdown(
                    f"""<div class="progress-bar" style="width: {progress}%;">
                    {progress}%
                </div>""",
                    unsafe_allow_html=True
                )
                
            time.sleep(1)    
            for (var, flag) in varName_ :
                j+=1
                
                # --------------
                
                #req ='node [name='+'"'+var+'"];out;'
                #req = 'nwr [name='+'"'+var+'"];(._;>;);out;'
                req = f"""(node[name='{var}'];
                              way[name='{var}'];
                              relation[name='{var}'];
                             );
                            ;"""
                compteurRequetes += 1
                requete = R.safe_query(req)
                res, i, batiments = R.requestToDict(requete, flag, nomInitial, res, i)
                compteurBatiments += batiments
                
                progress=j/max_length*100
                progress=round(progress)
                progress_container.markdown(
                    f"""<div class="progress-bar" style="width: {progress}%;">
                    {progress}%
                </div>""",
                    unsafe_allow_html=True
                )
            if res != {} :
                json.dump(res, f1)
                listeFichiers.append(fName+".json")
            print("Nombre de requêtes exécutées :",compteurRequetes)            
            print("Nombre de bâtiments trouvés :",compteurBatiments) 
        
        print("Temps de génération fichier/s :", str(round(temps-2))+" secondes.\n") #-2 car on a fait time.sleep(1)*2
        print(listeFichiers)
        return listeFichiers, []
