import geopandas as gpd

from shapely.geometry import Point


    
countries = gpd.read_file("country_worldwide/curiexplore-pays.shp")[["geometry", "name_fr"]]
gdf_countries = gpd.GeoDataFrame(countries)

def findCountry(df, Pays=[]):
    # 🔄 Convertir les latitudes/longitudes en objets géographiques (Points)
    # 🔄 Convertir les coordonnées en objets géographiques (Points)
    df["geometry"] = df.apply(lambda row: Point(float(row["Long"]), float(row["Lat"])), axis=1)
    gdf_out = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")

    # 🔗 Faire la jointure spatiale
    df = gpd.sjoin(gdf_out, gdf_countries, how="left", predicate="within")

    # ✅ Vérifier que la colonne 'name_fr' existe bien et la renommer en 'pays'
    if "name_fr" in df.columns : # Évite les problèmes de modification sur une vue
        df["pays"] = df["name_fr"]
        for pays in df["pays"] :
            if pays not in Pays :
                Pays.append(pays)
            
    else: "Inconnu"

    # 📝 Enregistrer le fichier CSV avec la colonne "pays"
    df.drop(columns=["geometry", "index_right", "name_fr"], inplace=True, errors="ignore")
    return df, Pays

