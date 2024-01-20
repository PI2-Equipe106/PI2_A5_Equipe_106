##### Code Python sous Streamlit d'une application permettant la tarification d'un contrat d'assurance inondation #####

# Liste des librairies et packages
import streamlit as st
from streamlit.logger import get_logger
import pandas as pd
from urllib.error import URLError
import altair as alt
import numpy as np
from geopy.distance import geodesic
from math import radians, sin, cos, sqrt, atan2
import geopy
import pydeck as pdk
import folium
from streamlit_folium import folium_static
import geocoder
from urllib.error import URLError
import altair as alt
import pandas as pd
import streamlit as st
from streamlit.hello.utils import show_code
import time
import geopandas as gpd
from pyproj import CRS
from shapely.geometry import Polygon, LineString
from shapely.ops import unary_union
import json
import zipfile
from zipfile import ZipFile
from io import BytesIO
import requests
import ast
from pyproj import Proj, transform
import re

# Lien vers les fichiers zips sur GitHub
url_zip = "https://raw.githubusercontent.com/PI2-Equipe106/PI2_A5_Equipe_106/main/Data_Application_Streamlit/liste_seuil_hauteur2.csv.zip"
url_zip2 = "https://raw.githubusercontent.com/PI2-Equipe106/PI2_A5_Equipe_106/main/Data_Application_Streamlit/Hydro_IDF_Polygon.csv.zip"

# Noms des fichier CSV à extraire des zips
nom_fichier_csv = "liste_seuil_hauteur2.csv"
nom_fichier_csv2 = "Hydro_IDF_Polygon.csv"

# Fonction pour lire les fichiers CSV depuis les zips
def lire_csv_depuis_zip(url_zip, nom_fichier_csv):
    response = requests.get(url_zip)
    with ZipFile(BytesIO(response.content)) as zip_file:
        with zip_file.open(nom_fichier_csv) as csv_file:
            return pd.read_csv(csv_file)

# Lecture du fichier des hauteurs historiques des stations et des polygons IDF (exemple)
donnees_historiques = lire_csv_depuis_zip(url_zip, nom_fichier_csv)
donnees_historiques = pd.DataFrame(donnees_historiques)
zones_hydro = lire_csv_depuis_zip(url_zip2, nom_fichier_csv2)
zones_hydro = pd.DataFrame(zones_hydro)
geometry = zones_hydro['geometry']
liste_geometry = geometry.tolist()

# Code pour la géolocalisation des locaux à partir de l'adresse renseignée
API_KEY = "Am2D925X03xaGU3LJ3is-D8tlsRIcwr_0otjXCLWeQCRGssNTJVn-E1FJA4RiO_w"
geolocator = geopy.geocoders.Bing(API_KEY)
def address_to_coordinates(address):
    location = geolocator.geocode(address)
    if hasattr(location, 'latitude') and hasattr(location, 'longitude'):
        return (location.latitude, location.longitude)
    else:
        return None
    
# Initialisation de la page avec le logo du partenaire et un accès au site web
LOGGER = get_logger(__name__)
image = "https://www.diot-siaci.com/wp-content/uploads/2023/01/RVB_DIOTSIACI_LOGOTYPE_MEDIUM.png"
st.image(image, use_column_width=True)
st.link_button("Diot-Siaci : Conseil et courtage d'assurance et de réassurance", "https://www.diot-siaci.com/")
st.write("\n")
st.write("\n")

# Chargement des fichiers csv nécessaires depuis le github
stations = pd.read_csv("https://raw.githubusercontent.com/PI2-Equipe106/PI2_A5_Equipe_106/main/Data_Application_Streamlit/Stations22.csv", delimiter=";")
#prediction = pd.read_csv("https://raw.githubusercontent.com/ThomJarland/testtjpie/main/prediction_exemple.csv", delimiter=",")
prededmee = pd.read_csv("https://raw.githubusercontent.com/PI2-Equipe106/PI2_A5_Equipe_106/main/Data_Application_Streamlit/predictions_edmee.csv", delimiter=";")
choixmodel = pd.read_csv("https://raw.githubusercontent.com/PI2-Equipe106/PI2_A5_Equipe_106/main/Data_Application_Streamlit/best_model.csv", delimiter=",")
Donnees_Modele_Maths = pd.read_csv("https://raw.githubusercontent.com/PI2-Equipe106/PI2_A5_Equipe_106/main/Data_Application_Streamlit/Donnees_Modele_Maths.csv", delimiter=";")
parametres_stations_VF= pd.read_csv("https://raw.githubusercontent.com/PI2-Equipe106/PI2_A5_Equipe_106/main/Data_Application_Streamlit/parametres_stations_VF.csv", delimiter=",")
probabilite_pi2_0_50= pd.read_csv("https://raw.githubusercontent.com/PI2-Equipe106/PI2_A5_Equipe_106/main/Data_Application_Streamlit/probabilite_pi2_0_50.csv", delimiter=";")

# Gestion de cohérence des stations disponibles dans chaque fichier csv
merged_df = pd.merge(stations, prededmee, how='inner', left_on='code_station', right_on='station')
stations = stations[stations['code_station'].isin(merged_df['code_station'])]
stations = stations[stations['code_station'].isin(donnees_historiques['code_station'])]
stations = stations[stations['code_station'].isin(choixmodel['station'])]
stations = stations[stations['code_station'].isin(Donnees_Modele_Maths['Station'])]
stations = stations[stations['code_station'].isin(parametres_stations_VF['station'])]
stations = stations[stations['code_station'].isin(probabilite_pi2_0_50['Station'])]

# Autorisation de géolocalisation / L'utilisateur renseigne son adresse
# En fonction de son adresse on retrouve ses coordonnées GPS, puis on peut trouver les 5 stations les plus proches du lieu 
on = st.toggle('J\'autorise l\'entreprise Diot-Siaci à géolocaliser les locaux que je souhaite assurer.')
if on:
    st.write("\n")
    st.subheader('Données géographiques :', divider='gray')
    test1=0
    test2=0
    try:
        countries = st.text_input('Entrez la ville dans laquelle vos locaux se situent :')
        if not countries:
            st.error("Veuillez entrez une ville valide")    
        else:
            test1 = 1   
    except URLError as e:
        st.error(""" **This demo requires internet access.** Connection error: %s """ % e.reason)
    if (test1 == 1):
        try:
            adresse = st.text_input('Entrez le numéro et la rue :')
            if not adresse:
                st.error("Veuillez entrez une adresse valide")    
            else:
                test2 = 1   
        except URLError as e:
            st.error(""" **This demo requires internet access.** Connection error: %s """ % e.reason)   
    if (test2 == 1):
        c="France"
        ma_liste = [adresse, countries, c]
        resultat = ", ".join(ma_liste)
        lieu = [resultat]
        coordinates = []
        for address in lieu:
            coordinate = address_to_coordinates(address)
            coordinates.append(coordinate)
        lat = coordinates[0][0]
        lon = coordinates[0][1]
        stations["Distance"] = -1
        stations = stations.dropna(subset=['libelle'])
        for i in stations.index:
            valeur_colonne1 = stations.at[i, 'longitude']
            valeur_colonne2 = stations.at[i, 'latitude']
            lat_A = radians(lat)
            lon_A = radians(lon)
            lat_B = radians(valeur_colonne2)
            lon_B = radians(valeur_colonne1)
            R = 6371.0
            dlat = lat_B - lat_A
            dlon = lon_B - lon_A
            a = sin(dlat / 2)**2 + cos(lat_A) * cos(lat_B) * sin(dlon / 2)**2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))
            distance = R * c
            stations.at[i, 'Distance'] = distance
        listeIndex = stations['Distance'].nsmallest(5).index
        indice_min = listeIndex[0]
        indice_min1 = listeIndex[1]
        indice_min2 = listeIndex[2]
        indice_min3 = listeIndex[3]
        indice_min4 = listeIndex[4]
        # On obtient ici le code des 5 stations les plus proches

        # On garde le code de la station la plus proche car c'est avec ce code qu'on va pouvoir retrouver les prédictions des modèles
        # ainsi que les données historiques
        id_min_distance = stations.at[indice_min, 'code_station']

        # On recupère les predictions du modèle séries temporelles
        valeur_pred_iuyo = prededmee.loc[prededmee['station'] == id_min_distance, 'predictoins'].values[0]

        # On recupère les données historiques et les dates associées
        histori = donnees_historiques.loc[donnees_historiques['code_station'] == id_min_distance, 'Résultat'].values[0]
        Dates = donnees_historiques.loc[donnees_historiques['code_station'] == id_min_distance, 'Dates'].values[0]

        # On choisit le meilleur modèle 
        choix = choixmodel.loc[choixmodel['station'] == id_min_distance, 'Modele'].values[0]

        # On garde uniquement les lignes de la station concernée (la plus proche)
        probabilite_pi2_0_50 = probabilite_pi2_0_50.loc[probabilite_pi2_0_50['Station'] == id_min_distance]
        parametres_stations_VF = parametres_stations_VF.loc[parametres_stations_VF['station'] == id_min_distance]
        Donnees_Modele_Maths = Donnees_Modele_Maths.loc[Donnees_Modele_Maths['Station'] == id_min_distance]
        
        # Nous avons des données du modèle mathématique en débit et non en hauteur, on convertit les débits associés en hauteur
        # grâce aux coefficients
        probabilite_pi2_0_50['Hauteur'] = ((parametres_stations_VF['a'].iloc[0])*probabilite_pi2_0_50['Seuil'])+(parametres_stations_VF['b'].iloc[0])
        probabilite_pi2_0_50['Hauteur']=round(probabilite_pi2_0_50['Hauteur'])

        # On créé la carte pour afficher le lieu à assurer ainsi que les 5 stations les plus proches
        valeur_minimale_A = stations.at[indice_min, 'Distance']
        valeur_associee_B = stations.at[indice_min, 'libelle']
        lon_station = stations.at[indice_min, 'longitude']
        lat_station = stations.at[indice_min, 'latitude']
        lon_station1 = stations.at[indice_min1, 'longitude']
        lat_station1 = stations.at[indice_min1, 'latitude']
        lon_station2 = stations.at[indice_min2, 'longitude']
        lat_station2 = stations.at[indice_min2, 'latitude']
        lon_station3 = stations.at[indice_min3, 'longitude']
        lat_station3 = stations.at[indice_min3, 'latitude']
        lon_station4 = stations.at[indice_min4, 'longitude']
        lat_station4 = stations.at[indice_min4, 'latitude']
        points = [
        {"latitude": lat, "longitude": lon, "label": "Locaux"},
        {"latitude": lat_station, "longitude": lon_station, "label": "Station"},
        {"latitude": lat_station1, "longitude": lon_station1, "label": "Station"},
        {"latitude": lat_station2, "longitude": lon_station2, "label": "Station"},
        {"latitude": lat_station3, "longitude": lon_station3, "label": "Station"},
        {"latitude": lat_station4, "longitude": lon_station4, "label": "Station"}]

        point_a_colorer = "Locaux"

        ma_carte = folium.Map(location=[points[0]["latitude"], points[0]["longitude"]], zoom_start=11)

        for point in points:

            if point["label"] == point_a_colorer:
                color = 'green'
                icon = "map-marker"
            else:
                color = 'blue'
                icon = "tint"
            marker = folium.Marker(location=[point["latitude"], point["longitude"]],popup=point["label"],
            icon=folium.Icon(color=color, icon=icon, prefix='fa'))
            marker.add_to(ma_carte)
        folium_static(ma_carte, width=700, height=500)

        # Polygons trop lourds et illisibles à mettre en place sur la carte
        # De plus, polygons des zones d'eau mais pas particulièrement à risque

        # On indique la station qui nous a permis de réalisée la tarification
        st.write(f"La station météorologique la plus proche est à {valeur_associee_B.capitalize()}, à {round(float(valeur_minimale_A),1)} kilomètres. C'est en partie avec cette station que nous avons évalué le risque inondation de vos locaux.")
        st.write("\n")

        # On affiche les données historiques
        st.subheader('Historique des données météorologiques :', divider='gray')              
        data_list = json.loads(histori)
        valeur_pred_iuyo=json.loads(valeur_pred_iuyo)
        premier_element = Dates[2:12]
        start_date = pd.to_datetime(premier_element)
        vecteur_dates = pd.date_range(start=start_date, periods=len(data_list), freq='D')
        df = pd.DataFrame({'Dates': vecteur_dates,'Hauteur (cm)': data_list})
        st.line_chart(df.set_index('Dates'))
        st.write("\n")

        # On demande la somme à assurer
        st.subheader('À propos de vos locaux :', divider='gray')
        number = st.number_input('Quel est le montant que vous souhaitez assurer pour vos locaux ?', value=None, placeholder="Entrez un nombre...", step=1)
        liste_decimaux = [float(nombre) for nombre in valeur_pred_iuyo]

        # Une fois que c'est renseignén, on demande la préférence de contrat pour le client
        if number :
            st.subheader('Vos préférences pour votre contrat :', divider='gray')
            genre = st.radio("",
            ["Je préfère choisir un seuil à partir duquel je serai indemnisé(e).", "Je préfère définir mon budget."],
            captions = ["Nous pourrons alors définir le prix de cette indemnisation.", "Nous pourrons alors définir le seuil à partir duquel vous serez indemnisé(e)."], index=None)

            # S'il choisit un seuil ...
            if genre == "Je préfère choisir un seuil à partir duquel je serai indemnisé(e).":
                
                # Si la station la plus proche a un meilleur résultat avec la série temporelle
                if choix == "Série temporelle":
                    def arrondir_sup_dizaine(nombre):
                        dizaine_sup = (nombre // 10 + 1) * 10
                        return int(round(dizaine_sup))
                    def arrondir_inf_dizaine(nombre):
                        dizaine_inf = (nombre // 10) * 10
                        return int(round(dizaine_inf))
                    
                    # On demande le seuil
                    st.subheader('Choix du seuil d\'indemnisation :', divider='gray')
                    seuil2 = st.slider('À partir de quel seuil souhaitez-vous être indemnisé ?', arrondir_sup_dizaine(min(liste_decimaux)), arrondir_inf_dizaine(max(liste_decimaux)), value=None,step=None)

                    if st.button("Je valide mon choix."):

                        #On réaffiche les données historiques avec le seuil choisit
                        st.subheader('Votre choix par rapport aux données historiques :', divider='gray')
                        df['Seuil choisi'] = seuil2
                        st.line_chart(df.set_index('Dates'))

                        # On affiche la proposition de contrat
                        # Prime = SA * % de dépassement du seuil
                        st.subheader('Notre proposition de contrat : ', divider='gray')
                        nombre_de_valeurs_superieures = sum(valeur >= seuil2 for valeur in liste_decimaux)
                        pourcentage = (nombre_de_valeurs_superieures/len(liste_decimaux))*100
                        sous=round((number*pourcentage)/100)
                        st.write(f"Adresse des locaux : {adresse}, {countries}.")
                        st.write(f"Somme assurée : {number} €.")
                        st.write(f"Seuil d'indemnisation : {seuil2} cm.")
                        st.write(f"Prix : {sous} €.")

                # Si la station la plus proche a un meilleur résultat avec le modèle mathématique
                if choix == "Modèle mathématiques":

                    # Choix du seuil
                    st.subheader('Choix du seuil d\'indemnisation :', divider='gray')
                    seuil2 = st.slider('À partir de quel seuil souhaitez-vous être indemnisé ?', round(min(probabilite_pi2_0_50['Hauteur'])), round(max(probabilite_pi2_0_50['Hauteur'])), value=None,step=(round((parametres_stations_VF['a'].iloc[0])*100)))
                    if st.button("Je valide mon choix."):
                        
                        # Affichage des données historiques et du seuil
                        st.subheader('Votre choix par rapport aux données historiques :', divider='gray')
                        df['Seuil choisi'] = seuil2
                        st.line_chart(df.set_index('Dates'))
                        
                        # Proposition de contrat
                        # Prime = SA * % de dépassement du seuil
                        st.subheader('Notre proposition de contrat : ', divider='gray')
                        index_plus_proche = (probabilite_pi2_0_50['Hauteur'] - seuil2).abs().idxmin()
                        sous = ((probabilite_pi2_0_50.loc[index_plus_proche, 'Seuil'])*number)/10000
                        sous = round(sous)
                        st.write(f"Adresse des locaux : {adresse}, {countries}.")
                        st.write(f"Somme assurée : {number} €.")
                        st.write(f"Seuil d'indemnisation : {seuil2} cm.")
                        st.write(f"Prix : {sous} €.")

            #S'il choisit un budget ...
            if genre == "Je préfère définir mon budget.":

                # Si la station la plus proche a un meilleur résultat avec la série temporelle
                if choix == "Série temporelle":

                    # Choix du budget
                    st.subheader('Choix de votre budget :', divider='gray')
                    number2 = st.slider('Quel est votre budget pour assurer vos locaux contre le risque inondation ?', 0, number, value=None,step=int(number/100))
                    if number2:
                        if st.button("Je valide mon choix."):
                            seuil_trouve = None

                            # On retrouve le seuil pour retrouver une probabilité correcte
                            for seuil_candidate in range(-10000, 10000):
                                nombre_de_valeurs_superieures2 = sum(valeur >= seuil_candidate for valeur in liste_decimaux)
                                prime_calculee = number * (nombre_de_valeurs_superieures2 / len(liste_decimaux))
                                
                                if abs(number2 - prime_calculee) < 30:
                                    seuil_trouve = seuil_candidate
                                    break
                            
                            if seuil_trouve is not None:
                                seuil_trouve = round(seuil_trouve)
                                st.subheader('Votre choix par rapport aux données historiques :', divider='gray')
                                df['Seuil choisi'] = seuil_trouve
                                st.line_chart(df.set_index('Dates'))

                                # Proposition de contrat
                                st.subheader('Notre proposition de contrat : ', divider='gray')
                                st.write(f"Adresse des locaux : {adresse}, {countries}.")
                                st.write(f"Somme assurée : {number} €.")
                                st.write(f"Seuil d'indemnisation : {seuil_trouve} cm.")
                                st.write(f"Prix : {number2} €.")

                            else:
                                st.write("Aucun seuil trouvé.")
                                st.write(prime_calculee)
                
                # Si la station la plus proche a un meilleur résultat avec le modèle mathématique
                if choix == "Modèle mathématiques":

                    # Choix du budget
                    st.subheader('Choix de votre budget :', divider='gray')
                    number2 = st.slider('Quel est votre budget pour assurer vos locaux contre le risque inondation ?', 0, number, value=None,step=int(number/100))
                    probabilite_pi2_0_50 = probabilite_pi2_0_50.reset_index(drop=True)
                    probabilite_pi2_0_50['Probabilite'] = probabilite_pi2_0_50['Probabilite'].str.rstrip('%')
                    probabilite_pi2_0_50['Probabilite'] = probabilite_pi2_0_50['Probabilite'].astype(int)

                    if number2:

                        if st.button("Je valide mon choix."):
                            seuil_trouve = None
                            probabilite_pi2_0_50 = probabilite_pi2_0_50.reset_index(drop=True)
                            probabilite_pi2_0_50['prime_calculee']=-1
                            for i in range(len(probabilite_pi2_0_50['Hauteur'])):
                                probabilite_pi2_0_50['prime_calculee'][i] = number * probabilite_pi2_0_50['Probabilite'][i]/100
                            
                            index_plus_proche = (probabilite_pi2_0_50['prime_calculee'] - number2).abs().idxmin()
                            seuil_trouve = round(probabilite_pi2_0_50.loc[index_plus_proche, 'Hauteur'])
                            
                            if seuil_trouve is not None:
                                st.subheader('Votre choix par rapport aux données historiques :', divider='gray')
                                df['Seuil choisi'] = seuil_trouve
                                st.line_chart(df.set_index('Dates'))

                                # Proposition de contrat
                                st.subheader('Notre proposition de contrat : ', divider='gray')
                                st.write(f"Adresse des locaux : {adresse}, {countries}.")
                                st.write(f"Somme assurée : {number} €.")
                                st.write(f"Seuil d'indemnisation : {seuil_trouve} cm.")
                                st.write(f"Prix : {number2} €.")

                            else:
                                st.write("Aucun seuil trouvé.")
