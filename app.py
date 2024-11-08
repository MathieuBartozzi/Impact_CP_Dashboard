import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import timedelta

# Configuration de la page
st.set_page_config(
    page_title="CP OSUI 2024 - 2025 ",
    layout="wide"
)

# # Charger les données depuis Google Sheets
# sheet_id = "10eH5dsJ2-t_ppLPgr9TIrijOR_1DdOYEPhSSiP6BhrI"
# sheet_name = "Feuille1"
# url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"


# # # Lire les données
# data = pd.read_csv(url)

# Utilisez @st.cache_data pour le chargement des données
@st.cache_data
def load_data():
    sheet_id = "10eH5dsJ2-t_ppLPgr9TIrijOR_1DdOYEPhSSiP6BhrI"
    sheet_name = "Feuille1"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    data = pd.read_csv(url)
    return data



# Nettoyer les données
@st.cache_data
def cleaning_data(data):
    colonnes_a_supprimer = ['Thèmes travaillés', 'Unnamed: 11', 'Unnamed: 12']
    data = data.drop(columns=colonnes_a_supprimer, errors='ignore')
    data['Durée (en heure)'] = pd.to_numeric(data['Durée (en heure)'], errors='coerce')
    data['Nombre d\'enseignants impactés'] = pd.to_numeric(data['Nombre d\'enseignants impactés'], errors='coerce')
    data['Efficacité perçue (1 : très faible ; 5 très haute)'] = pd.to_numeric(data['Efficacité perçue (1 : très faible ; 5 très haute)'], errors='coerce')
    data.rename(columns={'Efficacité perçue (1 : très faible ; 5 très haute)': 'Efficacité'}, inplace=True)
    data['Date'] = pd.to_datetime(data['Date'], format='%d/%m/%Y',errors='coerce')
    data['Durée (en heure)'].fillna(0, inplace=True)
    data['Nombre d\'enseignants impactés'].fillna(0, inplace=True)
    data['Efficacité'].fillna(0, inplace=True)
    data['Public'].fillna(0, inplace=True)
    data['Public'].replace('degré 1 et 2', 'inter degré', inplace=True)

    return data


# Chargement et nettoyage des données
data = load_data()
data_cleaned = cleaning_data(data)
# Convertir la colonne 'Date' en date uniquement pour la comparaison
data_cleaned['Date_only'] = data_cleaned['Date'].dt.date

# Convertir les dates en date uniquement (sans heure) pour le slider
date_min = data_cleaned['Date'].min().date()
date_max = data_cleaned['Date'].max().date()

#preparation data pour le chart avec les differents type de formations
repartition_type = data_cleaned['Type'].value_counts().reset_index()
repartition_type.columns = ['Type de Formation', 'Nombre']

#preparation data pour le chart avec les differents format de formations : presentiel/ligne
repartition_format = data_cleaned['Format'].value_counts().reset_index()
repartition_format.columns = ['Format', 'Nombre']

#preparation data pour le chart avec les differents public de formations : degré1/degré2
repartition_public = data_cleaned['Public'].value_counts().reset_index()
repartition_public.columns = ['Public', 'Nombre']

#calcul des metriques principales
total_interventions = len(data_cleaned)
total_enseignants = int(data_cleaned['Nombre d\'enseignants impactés'].sum())
duree_totale = data_cleaned['Durée (en heure)'].sum()
efficacite_moyenne_val = data_cleaned['Efficacité'].mean()

#theme des graphiques
color_grah_theme=px.colors.qualitative.T10

# Dictionnaire pour correspondre chaque public à une couleur spécifique
color_mapping_public= {
    'degré 1': '#F58518',  # orange par exemple
    'degré 2': '#4C78A8',  # bleu par exemple
    'inter degré': '#E45756'  # rouge par exemple pour 'inter degré'
}

# Titre principal
st.sidebar.title("CP OSUI 2024 - 2025 : tableau de bord d'activité ")

st.write("Répartition Format:", repartition_format)
st.write("Répartition Public:", repartition_public)
st.write("Data_cleaned:", data_cleaned)


# Slider de sélection de dates dans la barre latérale
selected_date_range = st.sidebar.slider(
    "Sélectionnez une plage de dates",
    min_value=date_min,
    max_value=date_max,
    value=(date_min, date_max),
    step=timedelta(days=1)
)


# Filtrer les données en fonction de la plage de dates sélectionnée
data_cleaned = data_cleaned[
    (data_cleaned['Date_only'] >= selected_date_range[0]) &
    (data_cleaned['Date_only'] <= selected_date_range[1])
]

# Debut de la page
# st.subheader("Indicateurs généraux")

#ligne 1 : indicateurs
col1, col2, col3, col4 = st.columns(4)
with col1:
    with st.container(border=True):
        st.metric(label="Nombre d'interventions", value=total_interventions)
with col2:
    with st.container(border=True):
        st.metric(label="Nombre d'enseignants impactés", value=total_enseignants)
with col3:
    with st.container(border=True):
        st.metric(label="Durée (en heure)", value=f"{duree_totale:.1f}")
with col4:
    with st.container(border=True):
        st.metric(label="Efficacité moyenne perçue (sur 5)", value=f"{efficacite_moyenne_val:.2f}")


#ligne 1 : pie chart formart + pie char format + repartation par public vs types.
col1, col2=st.columns([1, 3])
with col1:
        # Graphique en anneau pour la répartition des formats (sans légende pour éviter la répétition)
        fig_pie_format = px.pie(
            repartition_format,
            names='Format',
            values='Nombre',
            hole=.4,
            color_discrete_sequence=color_grah_theme
        )

        # Positionner le titre et supprimer la légende pour ce graphique
        fig_pie_format.update_layout(
            title_text="",
            legend=dict(
            orientation="h",  # Orientation horizontale
            yanchor="bottom",
            y=0.8,  # Positionner la légende au-dessus du graphique
            xanchor="center",
            x=0.5  # Centrer la légende
        ),
            margin=dict(t=20, b=0)
        )

        # Afficher le graphique
        st.plotly_chart(fig_pie_format)


with col2 :
        col1, col2 = st.columns([1, 2])

        with col1:
            # Graphique en anneau pour la répartition des formats (sans légende pour éviter la répétition)
            fig_pie_public = px.pie(
                repartition_public,
                names='Public',
                values='Nombre',
                hole=.4,
                color_discrete_map={
                'degré 1': '#F58518',  # orange
                'degré 2': '#4C78A8',  # bleu
                'inter degré': '#E45756'  # rouge
    }
            )

            # Positionner le titre et supprimer la légende pour ce graphique
            fig_pie_public.update_layout(
                title_text="",
                legend=dict(
                orientation="h",  # Orientation horizontale
                yanchor="bottom",
                y=0.8,  # Positionner la légende au-dessus du graphique
                xanchor="center",
                x=0.5  # Centrer la légende
            ),
                margin=dict(t=20, b=0)
            )
            # Afficher le graphique
            st.plotly_chart(fig_pie_public)

        with col2:
            fig_stacked_bar_degre = px.bar(
                data_cleaned,
                x="Nombre d'enseignants impactés",
                y='Type',
                color='Public',
                title=None,
                color_discrete_map={
                'degré 1': '#F58518',  # orange
                'degré 2': '#4C78A8',  # bleu
                'inter degré': '#E45756'  # rouge
    }
            )
            fig_stacked_bar_degre.update_layout(barmode='stack',showlegend=True)
            fig_stacked_bar_degre.update_xaxes(title=None)  # Supprimer le label de l'axe X
            fig_stacked_bar_degre.update_yaxes(title=None)  # Supprimer le label de l'axe Y

            st.plotly_chart(fig_stacked_bar_degre)


# Section 2 :
col1, col2 = st.columns(2)

with col1:
    #préparations des données
    data_expanded = data_cleaned.assign(
    Établissement_cible=data_cleaned['Établissement cible'].str.split(',')
    ).explode('Établissement_cible')
    data_expanded['Établissement_cible'] = data_expanded['Établissement_cible'].str.strip()

    # Calcul du nombre total d'enseignants impactés par établissement et tri par ordre décroissant
    impact_etablissement = (
        data_expanded.groupby('Établissement_cible')['Nombre d\'enseignants impactés']
        .sum()
        .reset_index()
        .sort_values(by='Nombre d\'enseignants impactés', ascending=False)
    )
    #visuel
    fig_chart_1 = px.bar(
        impact_etablissement,
        x='Établissement_cible',
        y='Nombre d\'enseignants impactés',
        title="Nombre d'enseignants impactés par établissement",
        color_discrete_sequence=color_grah_theme)
    # Suppression des titres des axes
    fig_chart_1.update_xaxes(title=None)
    fig_chart_1.update_yaxes(title=None)
    st.plotly_chart(fig_chart_1)

with col2:
    tendance = data_cleaned.groupby(pd.Grouper(key='Date')).agg({
        'Durée (en heure)': 'sum',
        'Nombre d\'enseignants impactés': 'sum'
    }).reset_index()

    # Trier par date
    tendance = tendance.sort_values(by='Date')

    # Calcul de la moyenne mobile sur la colonne 'Durée (en heure)' sur une fenêtre de 7 jours
    tendance['Moyenne_mobile'] = tendance['Durée (en heure)'].rolling(window=6).mean()

    # Visualisation
    fig_chart_2 = px.bar(
        tendance,
        x='Date',
        y='Durée (en heure)',
        title="Nombre d'heures d'intervention par jour",
        color_discrete_sequence=color_grah_theme
    )

    # Suppression des titres des axes
    fig_chart_2.update_xaxes(title=None, tickformat='%d/%m/%Y')
    fig_chart_2.update_yaxes(title="Durée (en heure)")

    # Ajout de la ligne de moyenne mobile
    fig_chart_2.add_scatter(
        x=tendance['Date'],
        y=tendance['Moyenne_mobile'],
        mode='lines',
        name='Moyenne mobile (7 jours)',
        showlegend=False,
        fill='tozeroy',
        line_shape='spline',
        line=dict(color=color_grah_theme[1], width=2)
    )

    # Affichage du graphique dans Streamlit
    st.plotly_chart(fig_chart_2)
