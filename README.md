# Projet python pour la data science : étude de la variation de la consommation d'électricité en fonction de la météo

 Auteurs : *Angela Grimaud, Alexandre Toux*  

## Sujet :
<div align="justify">
Arriver à anticiper le plus précisement possible les variations de la consommation d'électricité est un enjeu majeur pour les acteurs de ce secteur, qu'ils s'agisse des producteurs, tels qu'EDF, qui doivent ajuster la production à la demande et donc être capable d'anticiper les variations de consommation, ou bien des distributeurs, qui doivent également gérer les volumes d'électricités achetés aux producteurs afin de pouvoir fournir correctement leurs clients en électricité. 
L'objectif de ce projet est donc de proposer un modèle permettant de prédire, en utilisant à la fois des données historiques sur la consommation d'électricité, et des données météorologiques, la variation à court terme (c'est-à-dire sur des durées de l'ordre de l'heure) de la consommation d'électricité. 
Nous nous limiterons ici au cas de Paris, car nous disposons pour cette ville de données météorologiques et de consommation électrique locales et fiables. Toutefois la démarche que nous allons suivre pourrait tout à fait être adaptée et reproduite pour d'autres villes françaises.

## Problématique : 
Peut-on prédire les variations à court terme de la consommation d'électricité dans les métropoles françaises à partir des données historiques et météorologiques ?
 

## Données utilisées :
- [Consommation d'électricité des grandes Métropoles françaises temps réel](https://odre.opendatasoft.com/explore/dataset/eco2mix-metropoles-tr/information/?disjunctive.libelle_metropole&disjunctive.nature) : base de donnée produite par le transporteur national d'électricité, RTE, et publiée sur le site OpenData Réseaux-Énergies.  
- [Données climatologiques de base - horaires](https://www.data.gouv.fr/datasets/donnees-climatologiques-de-base-horaires) : données météo fournies par Météo France toutes les heures pour toutes les stations météorologiques du territoire national. Nous avons exploités les données des stations météorologiques parisiennes. 


## Navigation au sein du projet : 
L'essentiel de notre travail se situe au sein du dossier `notebooks`.

Le notebook `pred_conso.ipynb` propose une modélisation de la consommation électrique de la ville de Paris à partir des données historiques en recourant à la théorie des séries temporelles.

Le notebook `notebook_temperature.ipynb` prolonge et affine le travail de modélisation présenté dans le précédent notebook en prenant en compte les données de température. En première partie, il s'attèle à nettoyer et traiter les données issues des stations météorologiques, et en seconde partie il modélise la variation de consommation électrique en ajoutant les données météorologiques comme variable externe.

## Remarque sur la reproductibilité : 
Le fichier `requirements.txt` donne la liste des paquets dont l'installation est nécessaire au bon fonctionnement des différents scripts. 