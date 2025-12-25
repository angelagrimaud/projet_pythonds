import pandas as pd
import requests


#Importation des données de consommation electrique annuelles par département
urld = "https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/conso-departement-annuelle/exports/csv?lang=fr&timezone=Europe%2FBerlin&use_labels=true&delimiter=%3B"
conso_annuelle_departements = pd.read_csv(urld,sep=';')


#Importation des données de consommation electrique en temps réel pour la métropole de Paris (période 2020-2025)
url_paris = "https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/eco2mix-metropoles-tr/exports/csv?lang=fr&refine=libelle_metropole%3A%22M%C3%A9tropole%20du%20Grand%20Paris%22&facet=facet(name%3D%22libelle_metropole%22%2C%20disjunctive%3Dtrue)&timezone=Europe%2FParis&use_labels=true&delimiter=%3B"
df_paris = pd.read_csv(url_paris, sep=';')
