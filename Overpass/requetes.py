import overpy, time
from extractionDonnees import loadDatas

def get_overpass_data(company_name):
    """
    Interroge l'API Overpass avec overpy pour récupérer les données OSM d'une entreprise.
    """
    api = overpy.Overpass()
    query = f"""[out:json][timeout:180];(node["name"="{company_name}"];way["name"="{company_name}"];relation["name"="{company_name}"];);out center;"""  
    # Ajout de "out center;" pour forcer le centre des ways et relations

    try:
        result = api.query(query)
        return result
    except Exception as e:
        print(f"Erreur lors de la requête Overpass : {e}")
        return None

def process_osm_data(result):
    """
    Traite les données OSM pour extraire :
    - Les nodes avec leurs coordonnées
    - Le centre des ways et relations
    """
    results = []

    # Traitement des nœuds
    for node in result.nodes:
        results.append({
            "name": node.tags.get("name", "Unknown"),
            "type": "node",
            "latitude": float(node.lat),
            "longitude": float(node.lon)
        })

    # Traitement des ways (utilisation du "center" directement)
    for way in result.ways:
        if hasattr(way, "center_lat") and hasattr(way, "center_lon"):
            results.append({
                "name": way.tags.get("name", "Unknown"),
                "type": "way",
                "latitude": float(way.center_lat),
                "longitude": float(way.center_lon)
            })

    # Traitement des relations (utilisation du "center" si dispo)
    for relation in result.relations:
        if hasattr(relation, "center_lat") and hasattr(relation, "center_lon"):
            results.append({
                "name": relation.tags.get("name", "Unknown"),
                "type": "relation",
                "latitude": float(relation.center_lat),
                "longitude": float(relation.center_lon)
            })

    return pd.DataFrame(results)


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
            datas, coord = loadDatas(way, node = False)
            
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
            datas, coord = loadDatas(relation, node = False)
            
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

