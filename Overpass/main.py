import streamlit as st
import pandas as pd
import folium
from folium import IFrame
from streamlit_folium import folium_static
import plotly.graph_objects as go
import plotly.express as px
import os
import CSS as css
import mergeCountries as mc
import operationsCSV as _csv

# """ ADD TEXT HERE"""

css_path = os.path.join(os.path.dirname(__file__), "styles.css")
with open(css_path) as f:
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

# Fonction pour compter les occurrences (mise en cache pour optimiser)
@st.cache_data
def get_pays_counts(df):
    pays_counts = df["pays"].value_counts().reset_index()
    pays_counts.columns = ["pays", "count"]
    return pays_counts

    
def __main__(progress_container, option, NomEntreprise="", FichierCSV="") :
    listeFichiers, entreprise = [], ""
    dfOut = pd.DataFrame()
    download = "Preview (download available)"
    
    if option == NomEntreprise:
        entreprise = st.text_input("Company name")
        progress_container.markdown(
            '<span class="progress-bar-container">Loading ...<div class="progress-bar" id="progress"></div></span>',
            unsafe_allow_html=True
        )
        if entreprise != "":
            listeFichiers, _ = _csv.fromCSVtoJSON(option, progress_container, entreprise, "")
            dfOut = _csv.fromJSONtoDataFrame(listeFichiers)
            dfOut, Pays = mc.findCountry(dfOut)
            st.write(download)
            st.write(f"Results: {dfOut.shape[0]}")
            st.dataframe(dfOut)
            show_map(dfOut)
               
    elif option == FichierCSV:
        entreprise = "résultats entreprises"
        uploaded_file = st.file_uploader("Sélectionner un fichier CSV", type=["csv"])   
        progress_container.markdown(
            '<span class="progress-bar-container">Loading ...<div class="progress-bar" id="progress"></div></span>',
            unsafe_allow_html=True
        )
        
        if uploaded_file is not None:
            # Initialisation des variable
            listeFichiers_, entreprises = _csv.fromCSVtoJSON(option, progress_container, "", uploaded_file)
            listeFichiers += listeFichiers_
            
            dfOut = _csv.fromJSONtoDataFrame(listeFichiers)
            dfOut, Pays = mc.findCountry(dfOut)
            st.write(download)
            st.write(f"Results: {dfOut.shape[0]}")
            entreprises.pop()
            st.dataframe(dfOut)
            show_map(dfOut) 
    try:

        # 📌 2️⃣ Sélection des valeurs de la colonne "Name"
        selected_names = st.multiselect("Sélectionnez des lieux :", dfOut["Name"].unique(), default=dfOut["Name"].unique())
        
        # 📌 3️⃣ Filtrer le DataFrame en fonction de la sélection
        filtered_df = dfOut[dfOut["Name"].isin(selected_names)]
        
        # 📌 4️⃣ Récupérer les données mises en cache
        if not filtered_df.empty:
            pays_counts = get_pays_counts(filtered_df)
        
            # 📌 5️⃣ Limiter à 10 catégories max
            if len(pays_counts) > 10:
                top_pays = pays_counts.iloc[:10]  # Les 10 premiers
                other_count = pays_counts.iloc[10:]["count"].sum()  # Somme des autres
        
                # Ajouter une ligne "Autres" si nécessaire
                other_row = pd.DataFrame([["Autres", other_count]], columns=["pays", "count"])
                pays_counts = pd.concat([top_pays, other_row], ignore_index=True)
        
            # 📌 6️⃣ Créer et afficher le Pie Chart
            fig = px.pie(pays_counts, names="pays", values="count", title="Répartition par pays")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Aucune donnée disponible pour la sélection actuelle.")


        #TEST
         # 📌 1️⃣ Récupérer la liste unique des pays
        unique_pays = dfOut["pays"].unique()
        
        # 📌 2️⃣ Formulaire avec colonnes
        with st.form("selection_form"):
            st.write("### Sélectionnez les pays à afficher :")
        
            # Création des colonnes (on limite à 3 colonnes max pour une bonne lisibilité)
            cols = st.columns(min(len(unique_pays), 3))
        
            # Stocker les choix de l'utilisateur
            pays_selectionnes = {}
        
            # Affichage des cases à cocher pour chaque pays dans les colonnes
            for idx, pays in enumerate(unique_pays):
                col_idx = idx % 3  # Répartir sur 3 colonnes
                pays_selectionnes[pays] = cols[col_idx].checkbox(pays, value=True)
        
            # Bouton de soumission
            submitted = st.form_submit_button("Appliquer le filtre")
        
        # 📌 3️⃣ Filtrer le DataFrame en fonction de la sélection
        selected_pays = [p for p, checked in pays_selectionnes.items() if checked]
        filtered_df = dfOut[dfOut["pays"].isin(selected_pays)]
        
        if submitted and not filtered_df.empty:
            pays_counts = get_pays_counts(filtered_df)
        
            # 📌 5️⃣ Limiter à 10 catégories max
            if len(pays_counts) > 10:
                top_pays = pays_counts.iloc[:10]
                other_count = pays_counts.iloc[10:]["count"].sum()
                other_row = pd.DataFrame([["Autres", other_count]], columns=["pays", "count"])
                pays_counts = pd.concat([top_pays, other_row], ignore_index=True)
        
            # 📌 6️⃣ Afficher le Pie Chart
            fig = px.pie(pays_counts, names="pays", values="count", title="Répartition par pays")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Aucune donnée disponible pour la sélection actuelle.")

    
        
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
    #st.title("Cat'Map v2")
    st.image("Overpass/PNG/SquareManagement.png", width = 100)
    st.markdown("<h1 style='text-align: center; color: #bd8e43;'>Cat'Map v2</h1>", unsafe_allow_html=True)
    st.markdown('<div>', unsafe_allow_html=True)
    
    NomEntreprise = "Geolocation of company buildings by name"
    FichierCSV = "Geolocation of company buildings by csv file"
    option = st.radio("Select the chosen method :", (NomEntreprise, FichierCSV))
    st.write(option)
    
    # Conteneur pour la barre de progression
    barre_de_chargement = st.empty()
    
    # Exécuter la classe Test
    #T = Test(barre_de_chargement, option, NomEntreprise, FichierCSV)
    
    __main__(barre_de_chargement, option, NomEntreprise, FichierCSV)
    
    # Fin du bloc HTML
    st.markdown('</div>', unsafe_allow_html=True)
load()
