Projet académique - PI2

ESILV - ACTUARIAT - MASTER 2


Ce GitHub regroupe tous les éléments d’un projet académique visant à créer une application de cotation en assurance inondation. 

Ce projet a été découpé en 3 grandes étapes :

Webscrapping / récupération des données sur des sites open sources.
Modélisation : création de modèles mathématiques et de séries temporelles pour prédire le risque inondation pour les différentes stations dans la Database constituée.
Application : création d’une application streamlit pour permettre à un professionnel d’assurer ses locaux contre le risque inondation.

Explication de l’application : 

L’utilisateur arrive sur l’utilisation.
Il accepte que ses locaux soient géolocalisés.
Il rentre son adresse (ville, numéro et rue).
Une carte s’affiche avec les locaux indiqués ainsi que les 5 stations les plus proches autour de ses locaux.
S’affiche ensuite l’historique des données (en hauteur d’eau en cm) de la station la plus proche.
L’utilisateur renseigne ensuite la somme à assurer.
Il décide ensuite s’il préfère choisir un seuil et obtenir le prix correspondant, ou alors définir son budget et obtenir le seuil à partir duquel il sera indemnisé.
S’il choisit le seuil, il entre le seuil, s’affiche ensuite l’historique des données avec le seuil choisit afin que l’utilisateur ait une idée d’où se situe son seuil. En fonction des prédictions du modèle, on peut déterminer le tarif en multipliant la somme assurée par la probabilité de dépassement du seuil. Il obtient finalement le tarif.
S’il choisit un budget, c’est le calcul inverse, le modèle renvoie le seuil correspondant en fonction du budget, et on affiche les données historiques avec le seuil obtenu.
Finalement, on affiche les termes du contrat.
