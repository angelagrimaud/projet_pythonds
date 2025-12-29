import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
from datetime import date
import plotly.express as px
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from matplotlib.ticker import FuncFormatter
from statsmodels.tsa.stattools import adfuller


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


#définir saison
def saison(mois):
    if mois in [12, 1, 2]:
        return 'hiver'
    elif mois in [6, 7, 8]:
        return 'été'
    else:
        return 'printemps/automne'


#adaptation du df aux besoins de visualisation
def df_visual (df) :
    #on ne garde que la colonne conso
    df = df[['conso_final']].copy()
    
    #créer nouvelles colonnes
    df['heure_quart'] = df.index.hour + df.index.minute / 60
    df['heure'] = df.index.hour
    df['jour_semaine'] = df.index.day_name()  #en anglais
    df['is_weekend'] = df.index.weekday >= 5   #True/False
    df['mois'] = df.index.month
    df['saison'] = df['mois'].apply(saison)

    return df


def tendance(df, n=60) :
    window = n*96  #n jours = n*96 observations puisque 1 jour=96 observations
    
    df['moy'] = df['conso_final'].rolling(window=window, center=True, min_periods=window//2).mean()
    
    plt.figure(figsize=(14,5))
    plt.plot(df.index, df['conso_final'], alpha=0.15, label='Consommation brute')
    plt.plot(df.index, df['moy'], linewidth=2.5, label='Moyenne glissante sur ' + str(n) + ' jours')
    
    plt.title("Tendance de fond")
    plt.xlabel("Année")
    plt.ylabel("Consommation")
    plt.legend()
    plt.tight_layout()
    plt.show()


#formatter pour afficher les nombres en millions
def millions(x, pos):
    return f'{x/1e6:.1f} M'

#graphe des conso totales par année et par mois
def conso_tot(df) :
    formatter = FuncFormatter(millions)
    
    #conso annuelle
    yearly = df['conso_final'].resample('YE').sum()
    
    #conso mensuelle
    monthly_sum = df['conso_final'].groupby(df.index.month).sum()
    months = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc']
    
    #subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    #graph conso annuelle
    bars1 = ax1.bar(yearly.index.year, yearly.values, color='skyblue')
    ax1.set_title("Consommation annuelle")
    ax1.set_xlabel("Année")
    ax1.set_ylabel("Consommation")
    ax1.grid(axis='y', alpha=0.3)
    ax1.yaxis.set_major_formatter(formatter)
    ax1.bar_label(bars1, labels=[f'{v/1e6:.1f} M' for v in yearly.values], padding=3)
    
    #graph conso mensuelle
    bars2 = ax2.bar(months, monthly_sum.values, color='salmon')
    ax2.set_title("Consommation mensuelle cumulée sur la période")
    ax2.set_xlabel("Mois")
    ax2.set_ylabel("Consommation")
    ax2.grid(axis='y', alpha=0.3)
    ax2.yaxis.set_major_formatter(formatter)
    ax2.bar_label(bars2, labels=[f'{v/1e6:.1f} M' for v in monthly_sum.values], padding=3)
    
    plt.tight_layout()
    plt.show()


def heatmap(df) :
    #ordre des jours
    jours_ordre = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    #mise en forme des data
    heatmap_data = df.pivot_table(index='jour_semaine', columns='heure', values='conso_final', aggfunc='mean')
    heatmap_data = heatmap_data.reindex(jours_ordre)  # remettre dans l'ordre correct
    
    #heatmap
    plt.figure(figsize=(15, 6))
    sns.heatmap(heatmap_data, cmap='YlOrRd', annot=False)
    plt.title("Consommation électrique par jour de la semaine x heure")
    plt.xlabel("Heure")
    plt.ylabel("Jour de la semaine")
    plt.tight_layout()
    plt.show()


def profil_semaine_we (df) :
    profil_semaine = df[df['is_weekend']==False].groupby('heure_quart')['conso_final'].mean()
    profil_weekend = df[df['is_weekend']==True].groupby('heure_quart')['conso_final'].mean()
    
    plt.figure(figsize=(12,5))
    plt.plot(profil_semaine.index, profil_semaine.values, label='Semaine')
    plt.plot(profil_weekend.index, profil_weekend.values, label='Week-end')
    plt.xlabel("Heure")
    plt.ylabel("Consommation moyenne")
    plt.title("Profil journalier moyen : Semaine vs Week-end")
    plt.legend()
    plt.grid(True)
    plt.show()


def profil_jour_semaine(df) :
    jours_ordre = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    plt.figure(figsize=(12,6))
    for jour in jours_ordre:
        profil_jour = df[df['jour_semaine']==jour].groupby('heure_quart')['conso_final'].mean()
        plt.plot(profil_jour.index, profil_jour.values, label=jour)
    
    plt.xlabel("Heure")
    plt.ylabel("Consommation moyenne")
    plt.title("Profil journalier moyen par jour de la semaine")
    plt.legend()
    plt.grid(True)
    plt.show()

    
def profil_ete_hiver (df) :
    profil_ete = df[df['saison']=='été'].groupby('heure_quart')['conso_final'].mean()
    profil_hiver = df[df['saison']=='hiver'].groupby('heure_quart')['conso_final'].mean()
    
    plt.figure(figsize=(12,5))
    plt.plot(profil_ete.index, profil_ete.values, label='Été')
    plt.plot(profil_hiver.index, profil_hiver.values, label='Hiver')
    plt.xlabel("Heure")
    plt.ylabel("Consommation moyenne")
    plt.title("Profil journalier moyen : Été vs Hiver")
    plt.legend()
    plt.grid(True)
    plt.show()


#fonction testant la stationnarité d'une série au seuil de 5%
def adf_table(series, alpha=0.05):
    results = []
    dgp = {'n' : 'DGP1', 'c' : 'DGP2', 'ct' : 'DGP3'}

    for reg, label in dgp.items():
        adf_result = adfuller(series, regression=reg)

        adf_stat = adf_result[0]
        crit_value = adf_result[4]['5%']

        conclusion = "Stationnaire" if adf_stat < crit_value else "Non stationnaire"

        results.append({
            "DGP": label,
            "ADF statistic": adf_stat,
            "Valeur critique (5%)": crit_value,
            "Conclusion": conclusion
        })

    return pd.DataFrame(results)