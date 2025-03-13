import overpy, time
from extractionDonnees import loadDatas

class Requetes :
    # --- VARIABLE API --- #
    api = overpy.Overpass()

    def safe_query(query, api=api, retries=3, wait=5):
        for _ in range(retries):
            try:
                return api.query(query)
            except overpy.exception.OverpassGatewayTimeout:
                print("Timeout... Retry")
            except overpy.exception.OverpassUnknownContentType:
                print("Bad response... Retry")
            time.sleep(wait)
        raise Exception("No responses from Overpass API")
    
    def requestToDict(requete, flag, nomInitial, dictDatas = {}, i=1):
        """
        - Paramètre
        --------------------------------------------------------------------------------
        requete : 
            Type : class 'overpy.Result'
        
        - Retour
        --------------------------------------------------------------------------------
        Type de retour : tuple
        - dictDatas : 
            Type : dictionnaire
        - Twr : 
            Type : float
            
        Retourne un dictionnaire comprenant toutes les données de l'entreprise
        et ses établissements. Dont 4 tags significatifs et les coordonnées
        associées.
        Ainsi que le temps (en secondes) pour charger les données de l'API.

        """
        
        """
        dictOcc = []
        for element in requete:
            if element["type"] == "node":
                # Pour un nœud, on récupère directement ses coordonnées
                lat, lon = element["lat"], element["lon"]
                amenity =  element["amenity"]
                shop =  element["shop"]
            elif element["type"] in ["way", "relation"]:
                # Pour les ways et relations, on utilise le "center"
                if "center" in element:
                    lat, lon = element["center"]["lat"], element["center"]["lon"]
                    amenity =  element["amenity"]
                    shop =  element["shop"]
                else:
                    continue  # Si pas de centre, on ignore
            else:
                continue
        

            dictOcc.append({"name": element.get("tags", {}).get("name", "Unknown"),
                            "type": element["type"],
                            "latitude": lat,
                            "longitude": lon,
                            "amenity": amenity,
                            "shop": shop}
                          )
            i+= 1
        """
        
        """
        for occ in requete.nodes :
            dictOcc = {}
            
            datas, coord = loadDatas(occ)
            
            if datas["name"] != nomInitial :
                datas["name"]=nomInitial
            if datas["amenity"]==None:
                datas["amenity"]='X'
            if datas["shop"]==None:
                    datas["shop"]='X'
            # -----------------------------------------------------
            # création du dictionnaire
            dictOcc["coord"]=str(coord[0])+"/"+ str(coord[1])
            dictOcc["flag"]=str(flag)
            
            for data in datas :
                dictOcc[data] = datas[data]
            dictDatas["iteration "+str(i)]=dictOcc
            
            i+=1"""
            
        for occ in requete.nodes :
            dictOcc = {}
            
            datas, coord = loadDatas(occ)
            if datas["name"] != nomInitial :
                datas["name"]=nomInitial
            if datas["amenity"]==None:
                datas["amenity"]='X'
            if datas["shop"]==None:
                    datas["shop"]='X'
            # -----------------------------------------------------
            # création du dictionnaire
            dictOcc["coord"]=str(coord[0])+"/"+ str(coord[1])
            dictOcc["flag"]=str(flag)
            for data in datas :
                dictOcc[data] = datas[data]
            dictDatas["iteration "+str(i)]=dictOcc

        for way in requete.ways:
            dictOcc = {}
            datas, coord = loadDatas(way)
            
            if datas["name"] != nomInitial:
                datas["name"] = nomInitial
            if datas["amenity"] is None:
                datas["amenity"] = 'X'
            if datas["shop"] is None:
                datas["shop"] = 'X'
            
            # Création du dictionnaire pour les ways
            dictOcc["coord"] = str(coord[0]) + "/" + str(coord[1])
            dictOcc["flag"] = str(flag)
            
            for data in datas:
                dictOcc[data] = datas[data]
            
            dictDatas["iteration " + str(i)] = dictOcc
            i += 1
    
        # Traitement des relations
        for relation in requete.relations:
            dictOcc = {}
            datas, coord = loadDatas(relation)
            
            if datas["name"] != nomInitial:
                datas["name"] = nomInitial
            if datas["amenity"] is None:
                datas["amenity"] = 'X'
            if datas["shop"] is None:
                datas["shop"] = 'X'
            
            # Création du dictionnaire pour les relations
            dictOcc["coord"] = str(coord[0]) + "/" + str(coord[1])
            dictOcc["flag"] = str(flag)
            
            for data in datas:
                dictOcc[data] = datas[data]
            
            dictDatas["iteration " + str(i)] = dictOcc
                    
            i+=1
            buildings = len(requete.nodes) + len(requete.ways) + len(requete.relations)
        return dictDatas, i, buildings

