import streamlit as st
import pandas as pd
import folium
from folium import IFrame
from streamlit_folium import folium_static

import plotly.graph_objects as go
import os
import CSS as css

"""
Essaye de mettre « pays » en variable maintenant dans un bouton
|_-> Filter le chart par pays
"""

import mergeCountries as mc
import operationsCSV as _csv

with open("styles.css") as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
def pieChart(pays,entreprise, _effectif, effectif) :
    
    EffectifMax = sum(effectif)
    seuil = int(0.02 * EffectifMax)
    
    _effectif = _effectif[_effectif >= seuil]
    
    
    fig = go.Figure(
        data=[go.Pie(labels=_effectif.index, values=_effectif, hole=0.3)],
        layout_title_text=f"""PieChart {entreprise}"""
    )
    return fig

    
def __main__(progress_container, option, NomEntreprise="", FichierCSV="") :
    
    listeFichiers, entreprise = [], ""
    dfOut = pd.DataFrame()
    download = "Vous pouvez télécharger le tableau ci-dessous avec un bouton en laissant la souris sur le coin à droite du tableau (dernière colonne)."
    if option == NomEntreprise:
        entreprise = st.text_input("Nom de l'entreprise")
        progress_container.markdown(
            '<span class="progress-bar-container">Chargement des données<div class="progress-bar" id="progress"></div></span>',
            unsafe_allow_html=True
        )
        if entreprise != "":
            listeFichiers, _ = _csv.fromCSVtoJSON(option, progress_container, entreprise, "")
            dfOut = _csv.fromJSONtoDataFrame(listeFichiers)
            dfOut, Pays = mc.findCountry(dfOut)
            st.write(download)
            """dataframe: CSV out"""
            st.dataframe(dfOut)
            show_map(dfOut)
            
    
    elif option == FichierCSV:
        entreprise = "résultats entreprises"
        uploaded_file = st.file_uploader("Sélectionner un fichier CSV", type=["csv"])
        
        progress_container.markdown(
            '<span class="progress-bar-container">Chargement des données<div class="progress-bar" id="progress"></div></span>',
            unsafe_allow_html=True
        )
        
        if uploaded_file is not None:
            
            # Initialisation des variable
            
            
            listeFichiers_, entreprises = _csv.fromCSVtoJSON(option, progress_container, "", uploaded_file)
            listeFichiers+=listeFichiers_
                
            dfOut = _csv.fromJSONtoDataFrame(listeFichiers)
            dfOut, Pays = mc.findCountry(dfOut)
            st.write(download)
            
            entreprises.pop()
            st.dataframe(dfOut)
            show_map(dfOut) 
    try:
        """onglets = st.tabs(Pays)"""
        Pays = Pays[:5]
        onglets = st.tabs(Pays)
        
                
        effectif = dfOut["pays"].value_counts()
        
        
        #TODO : le % est calculé sur la population post filtre et non initiale
        
        st.plotly_chart(pieChart(dfOut["pays"], entreprise, effectif, effectif))
        i=0
        for pays in Pays :
            with onglets[i]:
                
                st.header("Graphique PieChart "+pays)
                dfFiltrePays = pd.DataFrame()
                ##### graph à supprimer 
                dfFiltrePays["pays"] = dfOut["pays"].apply(lambda p: p if p == pays else "Autre")
                _effectif = dfFiltrePays["pays"].value_counts()
                
                
                
                
                       
                st.plotly_chart(pieChart(dfFiltrePays["pays"], entreprise, _effectif, effectif))
                
            i+=1
            st.write(pays)
                
                
                
        
    except:
        pass
            
    
    for JSON in listeFichiers :
        os.remove("json/"+JSON)
            
    



def show_map(df):
    m = folium.Map(location=[48.8566, 2.3522], zoom_start=5)
    occ = 0
    for _, row in df.iterrows():
        
        if occ >500 :
            break
        
        _popup=row["Lat"]+" "+row["Long"]+"\n"
        _popup +="Name:"+row["Name"]+"\n"
        _popup += "Amenity:"+row["Amenity"]
        
        cssClassPopup = css.__CssClassPopup()
        _popup = f"""
        <div style="{cssClassPopup}">
            {_popup}
        </div>"""
            
        iframe = IFrame(_popup, width=105, height=80)  # Ajuster la taille ici
        popup = folium.Popup(iframe, max_width=250)  # Ajuster la largeur max du popup
        folium.CircleMarker(
            location=[float(row["Lat"]), float(row["Long"])],
            radius=6,
            weight=0,
            color="blue",
            fill=True,
            fill_color="blue",
            fill_opacity=0.6,
            popup=popup
        ).add_to(m)
        occ+=1
    folium_static(m)
    
def load() :
    st.title("Recherche d'entreprises avec Overpass Turbo")
    st.markdown('<div>', unsafe_allow_html=True)
    NomEntreprise = "Générer un fichier CSV pour une seule entreprise"
    FichierCSV = "Générer un fichier CSV depuis un autre fichier du même format"
    option = st.radio("Choisissez une option :", (NomEntreprise, FichierCSV))
    st.write(option)
    
    # Conteneur pour la barre de progression
    barre_de_chargement = st.empty()
    
    # Exécuter la classe Test
    #T = Test(barre_de_chargement, option, NomEntreprise, FichierCSV)
    
    __main__(barre_de_chargement, option, NomEntreprise, FichierCSV)
    
    # Fin du bloc HTML
    st.markdown('</div>', unsafe_allow_html=True)
load()
