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

def show_map(df):
    m = folium.Map(location=[48.8566, 2.3522], zoom_start=5)
    occ = 0
    for _, row in df.iterrows():
        #if occ >500 :
            #break
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
            st.write(f"Results: {listeFichiers.shape[0]}")
            st.write(listeFichiers)
            #dfOut = _csv.fromJSONtoDataFrame(listeFichiers)
            dfOut, Pays = mc.findCountry(listeFichiers)
            st.write(download)
            st.write(f"Results: {dfOut.shape[0]}")
            st.dataframe(dfOut)
            show_map(dfOut)
               
    elif option == FichierCSV:
        entreprise = "résultats entreprises"
        uploaded_file = st.file_uploader("Select CSV file", type=["csv"])   
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
        if dfOut is not None:
            st.session_state.dfOut = dfOut
        else:
            st.write("Erreur : dfOut is void")
        col_fig1, col_fig2 = st.columns(2)
        
        with col_fig1:
            # Interface utilisateur - Sélection des "Name"
            #st.write("Select companie(s)")
            with st.expander("Select companie(s)", expanded=False):
                selected_names = st.multiselect(
                    "Companie(s):", 
                    options=st.session_state.dfOut["Name"].unique(),
                    default=st.session_state.dfOut["Name"].unique()  # Tout sélectionné par défaut
                )
            # Appliquer le filtre sur dfOut
            filtered_df = st.session_state.dfOut[st.session_state.dfOut["Name"].isin(selected_names)]
            pays_counts = get_pays_counts(filtered_df)
        
            # Limiter à 10 catégories max
            if len(pays_counts) > 10:
                top_pays = pays_counts.iloc[:10]
                other_count = pays_counts.iloc[10:]["count"].sum()
                other_row = pd.DataFrame([["Autres", other_count]], columns=["pays", "count"])
                pays_counts = pd.concat([top_pays, other_row], ignore_index=True)
                
            # Afficher le Pie Chart
            # Création des colonnes pour la mise en page
            fig = px.pie(pays_counts, names="pays", values="count")
            fig.update_layout(
                legend=dict(font=dict(size=8)),
                margin=dict(l=5, r=50)
            )
            fig.update_traces(texttemplate="%{percent:.0%}")
            st.plotly_chart(fig, use_container_width=True)


        with col_fig2:
            # Interface utilisateur - Sélection des "Name"
            #st.write("Select type(s) of businness")
            with st.expander("Select type(s) of businness:", expanded=False):
                selected_business = st.multiselect(
                    "type(s) of businness:", 
                    options=st.session_state.dfOut["Amenity"].unique(),
                    default=st.session_state.dfOut["Amenity"].unique()  # Tout sélectionné par défaut
                )
            # Appliquer le filtre sur dfOut
            filtered_df2 = st.session_state.dfOut[st.session_state.dfOut["Amenity"].isin(selected_business)]
            pays_counts2 = get_pays_counts(filtered_df2)
        
            # Limiter à 10 catégories max
            if len(pays_counts2) > 10:
                top_pays2 = pays_counts2.iloc[:10]
                other_count2 = pays_counts2.iloc[10:]["count"].sum()
                other_row2 = pd.DataFrame([["Autres", other_count2]], columns=["pays", "count"])
                pays_counts2 = pd.concat([top_pays2, other_row2], ignore_index=True)
                
            # Afficher le Pie Chart
            # Création des colonnes pour la mise en page
            fig2 = px.pie(pays_counts2, names="pays", values="count")
            fig2.update_layout(
                legend=dict(font=dict(size=8)),
                margin=dict(l=5, r=50))
            fig2.update_traces(texttemplate="%{percent:.0%}")
            st.plotly_chart(fig2, use_container_width=True)
        
    except:
        pass
    
    for JSON in listeFichiers :
        os.remove("json/"+JSON)
    
def load() :
    # Création de la disposition en trois colonnes
    col1, col2, col3 = st.columns([1, 4, 1])  # Colonnes de tailles différentes
    with col2:
        st.image("Overpass/PNG/TopBanner.png", width=1500)
    
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
