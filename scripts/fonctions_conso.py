import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
from datetime import date
import plotly.express as px
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from matplotlib.ticker import FuncFormatter


#importation du df
def importation(url) :
    return pd.read_csv(url, sep=';')
    
    
#nettoyage structurel du df
def clean(df) :
    #supprimer les observations correspondant à la date du jour (selon l'heure de chargement, nombreuses valeurs manquantes)
    df = df.loc[df['Date'] != str(date.today())].copy()
    
    #convertir en format date
    df['date'] = pd.to_datetime(df['Date'])
    df['date_heure'] = pd.to_datetime(df['Date'] + ' ' + df['Heures'])

    #placer la colonne date_heure en index et trier
    df = (df.set_index('date_heure').sort_index())

    #renommer les colonnes selon les conventions (ex : _ remplace l'espace) 
    df = df.rename(columns={'Code métropole': 'code_met', 'Métropole': 'met', 'Consommation (MW)' : 'conso', 'Heures' : 'heure'})

    #remplacer les conso de 0 par des NaN
    df['conso'] = df['conso'].replace(0, np.nan)

    #conserver uniquement les colonnes utiles et réordonner les colonnes
    df = df[['code_met', 'met', 'date', 'heure', 'conso']]
    
    return df


#reconstruction des valeurs manquantes
def traitement_valeurs_manquantes (df):
    #interpolation pour les petites plages de données
    df['conso_interp'] = df['conso'].interpolate(method='time', limit=4, limit_direction='both')

    #reconstruction via J-7 pour les plages de données plus importantes
    df['conso_final'] = df['conso_interp'].fillna(df['conso'].shift(96 * 7))

    return df


#graphique affichant la reconstruction des valeurs manquantes sur la période sélectionnée
def graph_valeurs_manquantes (start, end, df) :    
    df_zoom = df.loc[start:end].copy()
    x = df_zoom.index
    y = df_zoom["conso_final"].values
    
    #on met True pour les données initiales et False pour les données reconstruites afin de les afficher dans des couleurs différentes
    is_initial = df_zoom["conso"].notna().values
    
    #graphe
    fig = go.Figure()
    
    for i in range(len(x) - 1):
        color = "green" if is_initial[i] else "red"
        
        fig.add_trace(go.Scatter(
            x=[x[i], x[i+1]],
            y=[y[i], y[i+1]],
            mode="lines",
            line=dict(color=color, width=2),
            showlegend=False,
            hoverinfo="skip"))
    
    fig.update_layout(
        title="Consommation électrique, données initiales vs reconstruites",
        xaxis_title="Date",
        yaxis_title="Consommation",
        template="plotly_white")
    
    fig.show()


#df des statistiques descriptives 
def stats_desc(df) :
    stats_desc = {
    'Moyenne': df['conso_final'].mean(),
    'Médiane': df['conso_final'].median(),
    'Mode': df['conso_final'].mode()[0],
    'Min': df['conso_final'].min(),
    'Max': df['conso_final'].max(),
    'Amplitude': df['conso_final'].max() - df['conso_final'].min(),
    'Écart-type': df['conso_final'].std(),
    'Variance': df['conso_final'].var(),
    'Skewness': stats.skew(df['conso_final']),
    'Kurtosis': stats.kurtosis(df['conso_final'])}

    return pd.DataFrame(stats_desc, index=['Valeur']).round(2)


#visualition des données
def graph(startdate, enddate, df) : 
    #filtrer les données selon la plage choisie
    filtered_data = df[(df.index >= startdate) & (df.index <= enddate)]
    
    #calculer la longueur de la plage choisie pour afficher la légende de l'axe des abscisses en conséquence
    date_diff = pd.to_datetime(enddate) - pd.to_datetime(startdate)
    
    #graphe
    fig = px.line(filtered_data, x=filtered_data.index, y='conso_final', 
                  labels={'date_heure':'Date', 'conso_final':'Consommation (MW)'})
    
    #affichage de l'axe des abscisses
    if date_diff.days <= 365:  #plage de moins d'un an => on affiche les mois
        fig.update_xaxes(dtick='M1', tickformat='%b %Y') 
    else:  #plage de plus d'un an => on affiche les années
        fig.update_xaxes(dtick='M12',tickformat='%Y')
    fig.update_xaxes(range=[startdate, enddate])
    
    #on ajuste l'axe des ordonnées selon le min et le max de la plage choisie
    fig.update_yaxes(range=[filtered_data['conso_final'].min(), filtered_data['conso_final'].max()])
    
    #taille du graphe
    fig.update_layout(width=850, height=400, title='Consommation électrique de la ' + str(df['met'].iloc[0]))
    
    fig.show()