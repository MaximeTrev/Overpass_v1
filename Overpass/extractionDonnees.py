# -*- coding: utf-8 -*-

import overpy
import streamlit as st
    
def loadDatas(node_data):
    if isinstance(node_data, overpy.Node):
        lat = node_data.lat
        lon = node_data.lon
        amenity = node_data.tags.get("amenity")
        shop = node_data.tags.get("shop")
        return {"id": node_data.id, "name": node_data.tags.get("name", "Nom inconnu"),    
                "amenity": amenity,
                "shop" : shop
                }, (lat,lon)
    
    
