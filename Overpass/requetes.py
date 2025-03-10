# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 15:47:34 2025

@author: jerome.hertzog_squar
"""

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
                print("Timeout, on réessaie...")
            except overpy.exception.OverpassUnknownContentType:
                print("Mauvaise réponse, on réessaie...")
            time.sleep(wait)
        raise Exception("Overpass API ne répond pas après plusieurs tentatives")
    
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
        
        #print("Nombre de batiments :", len(requete.nodes))
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
            
            i+=1
        return dictDatas, i, len(requete.nodes)

