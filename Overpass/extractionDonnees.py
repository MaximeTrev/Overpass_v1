# -*- coding: utf-8 -*-

import overpy
import streamlit as st
    
def loadDatas(data, node = True):
    if node:
        lat = data.lat
        lon = data.lon
    else:
        lat = data.center["lat"]
        lon = data.center["lon"]
    amenity = data.tags.get("amenity")
    shop = data.tags.get("shop")
    return {"id": data.id, "name": data.tags.get("name", "Nom inconnu"),    
            "amenity": amenity,
            "shop" : shop
            }, (lat,lon)
    
    
