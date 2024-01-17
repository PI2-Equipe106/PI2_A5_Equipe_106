library(lubridate)
library(ggplot2)
library(xlsx)
library(tidyverse)
library(plotly)
library(forecast)
library(zoo)
library(readr)
library(dplyr)

setwd("/Users/thomasjarland/Documents/Master 2/Time series")
chemin_repertoire_hauteur <- "/Users/thomasjarland/Documents/Master 2/Time series/data_stations_hauteur"
chemin_repertoire_debit <- "/Users/thomasjarland/Documents/Master 2/Time series/data_stations_debit"
fichiers_csv_hauteur <- list.files(path = chemin_repertoire_hauteur, pattern = "\\.csv$", full.names = TRUE)
fichiers_csv_debit <- list.files(path = chemin_repertoire_debit, pattern = "\\.csv$", full.names = TRUE)

# Définir les noms des colonnes
noms_colonnes <- c("station", "a", "b")

# Créer un dataframe pour stocker les paramètres des stations
parametres_stations <- data.frame(matrix(nrow = length(fichiers_csv_hauteur), ncol = length(noms_colonnes)))
colnames(parametres_stations) <- noms_colonnes
count=1
for (i in seq_along(fichiers_csv_hauteur)) {
  seuil_file_name <- basename(fichiers_csv_hauteur[i])
  #cat(i)
  if (seuil_file_name %in% basename(fichiers_csv_debit)) {
    print("validation")
    print(i)
    index_debit <- which(basename(fichiers_csv_debit) == seuil_file_name)
    print(i)
    df2 <- read.csv(fichiers_csv_debit[index_debit])
    df1 <- read.csv(fichiers_csv_hauteur[i])
    print(i)
    
    code = df1[1, 1]
    print(code)
    
    df1$jour <- substr(df1$date_debut_serie, 1, 10)
    df2$jour <- substr(df2$date_debut_serie, 1, 10)
    print(i)
    df1 <- df1 %>%
      select(-c(date_debut_serie, date_fin_serie, date_obs, continuite_obs_hydro))
    df2 <- df2 %>%
      select(-c(date_debut_serie, date_fin_serie, date_obs, continuite_obs_hydro))
    print(i)
    df1 <- df1 %>%
      group_by(jour) %>%
      summarise(resultat_obs = mean(resultat_obs))
    df2 <- df2 %>%
      group_by(jour) %>%
      summarise(resultat_obs = mean(resultat_obs))
    print(i)
    resultat2 <- merge(df1, df2, by='jour')
    if (nrow(resultat2) < 1) {
      cat("Avertissement : Pas assez d'observations pour ajuster le modèle pour", seuil_file_name, ". Ignoré.\n")
      next  # Passer à l'itération suivante de la boucle
    }
    print(i)
    coefficients <- lm(resultat_obs.x ~ resultat_obs.y, data=resultat2)$coefficients
    slope <- coefficients[2]
    intercept <- coefficients[1]
    print(i)
    parametres_stations[count, 1] <- code
    parametres_stations[count, 2] <- slope
    parametres_stations[count, 3] <- intercept
    count=count+1
    cat("fin")
  }
}

parametres_stations_VF <- na.omit(parametres_stations)
write.csv(parametres_stations_VF, file = "parametres_stations_VF.csv", row.names = FALSE)