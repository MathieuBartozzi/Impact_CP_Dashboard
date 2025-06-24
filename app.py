import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import timedelta

# Configuration de la page
st.set_page_config(
    page_title="CP OSUI 2024 - 2025 ",
    layout="wide"
)

st.logo('logo.png')


def load_sheet(file_id, gid):
    url = f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=csv&gid={gid}"
    df = pd.read_csv(url)
    return df

# Charger chaque onglet dans un DataFrame
file_id_avis_de_mission = "1iEPI3UaPmMzDF1SpHAmR6ghlScBH1gC3FFWdn8MLH8U"
file_id_impact_cp="10eH5dsJ2-t_ppLPgr9TIrijOR_1DdOYEPhSSiP6BhrI"
gid = {
    "avis_de_mission": "90394237",
    "impact_cp": "0"
}

# Titre principal
st.title("CP OSUI 2024 - 2025 : tableau de bord d'activité ")

tab1, tab2= st.tabs(["**AVIS DE MISSION**", "**ACTIVITÉ DE L'ÉQUIPE**"])

############################## ACTIVITÉ DE L'ÉQUIPE  ##############################
with tab2 :
    # Nettoyer les données
    @st.cache_data
    def cleaning_data_impact_cp(data):
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
    data = load_sheet(file_id_impact_cp,gid['impact_cp'])
    data_cleaned_impact_cp = cleaning_data_impact_cp(data)

    # Convertir la colonne 'Date' en date uniquement pour la comparaison
    data_cleaned_impact_cp['Date_only'] = data_cleaned_impact_cp['Date'].dt.date

    # # Titre principal
    # st.title("CP OSUI 2024 - 2025 : tableau de bord d'activité ")

    #calcul des metriques principales
    total_interventions = len(data_cleaned_impact_cp)
    total_enseignants = int(data_cleaned_impact_cp['Nombre d\'enseignants impactés'].sum())
    duree_totale = data_cleaned_impact_cp['Durée (en heure)'].sum()
    # Calcul des dates minimale et maximale
    min_date = data_cleaned_impact_cp['Date'].min()
    max_date = data_cleaned_impact_cp['Date'].max()


    # Calcul du nombre de semaines
    num_weeks = (max_date - min_date).days // 7
    nb_cp=12
    durée_moyenne=round(duree_totale/num_weeks/nb_cp,2)

    # Debut de la page

    #ligne 1 : indicateurs
    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container(border=True):
            st.metric(label="Nombre total d'interventions des CP", value=total_interventions)
    with col2:
        with st.container(border=True):
            nb_total_enseignants=883
            # st.metric(label="Taux moyen d'exposition des enseignants aux CP", value=round(total_enseignants/nb_total_enseignants,2))
                # Calcul pondéré réel
            data_cleaned_impact_cp["impact_duree"] = (
                data_cleaned_impact_cp["Durée (en heure)"] * data_cleaned_impact_cp["Nombre d'enseignants impactés"]
            )
            total_heures_enseignants = data_cleaned_impact_cp["impact_duree"].sum()
            taux_duree_par_enseignant = total_heures_enseignants / nb_total_enseignants
            # Affichage dans un bloc de métrique
            st.metric(
                label="Durée moyenne d'accompagnement par enseignant (en h)",
                value=round(taux_duree_par_enseignant, 2),
                help="Somme pondérée des heures réparties sur l'ensemble des enseignants du réseau"
            )
    with col3:
        with st.container(border=True):
            st.metric(label="Durée moyenne d'intervention hebdomadaire par CP (en h)", value=durée_moyenne)
    # with col4:
    #     with st.container(border=True):
    #         st.metric(label="Efficacité moyenne perçue (sur 5)", value=f"{efficacite_moyenne_val:.2f}")


    #ligne 1 : pie chart formart + pie char format + repartation par public vs types.
    col1, col2=st.columns([1, 3])
    with col1:
        with st.container(border=True):

            @st.cache_data
            def presentiel_distanciel_global(df):
                """
                Affiche un graphique en pie chart pour la répartition des formats (présentiel/distanciel).

                Args:
                    df (pd.DataFrame): Le DataFrame contenant les données des missions.

                Returns:
                    None: Affiche directement le graphique dans Streamlit.
                """
                # Préparation des données pour le graphique
                repartition_format = df['Format'].value_counts().reset_index()
                repartition_format.columns = ['Format', 'Nombre']

                # Créer le graphique en pie chart
                fig_pie_format = px.pie(
                    repartition_format,
                    names='Format',
                    values='Nombre',
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.T10
                )

                # Positionner le titre et supprimer la légende pour ce graphique
                fig_pie_format.update_layout(
                    width=300, height=200,
                    legend=dict(
                        orientation="h",  # Orientation horizontale
                        yanchor="bottom",
                        xanchor="center",
                        x=0.5,
                        y=-0.5  # Centrer la légende en bas
                    ),
                    margin=dict(t=0, b=0)  # Réduction des marges
                )

                # Afficher le graphique dans Streamlit
                st.plotly_chart(fig_pie_format)

            presentiel_distanciel_global(data_cleaned_impact_cp)

    with col2 :

        with st.container(border=True):
            col1, col2 = st.columns([1, 2])

            with col1:

                t10_colors = px.colors.qualitative.T10
                color_mapping_public = {
                    'degré 1': t10_colors[0],  # Bleu
                    'degré 2': t10_colors[1],  # Orange
                    'inter degré': t10_colors[2],  # Vert
                    'autre': t10_colors[3]
                }
                @st.cache_data
                def repartition_public_global(data_cleaned_impact_cp):
                    """
                    Affiche un graphique en pie chart pour la répartition des publics (degré 1, degré 2, inter degré).

                    Args:
                        data_cleaned_impact_cp (pd.DataFrame): Le DataFrame contenant les données des missions, incluant une colonne 'Public'.

                    Returns:
                        None: Affiche directement le graphique dans Streamlit.
                    """
                    # Préparation des données pour le graphique
                    repartition_public = data_cleaned_impact_cp['Public'].value_counts().reset_index()
                    repartition_public.columns = ['Public', 'Nombre']

                    # Créer le graphique en pie chart
                    fig_pie_public = px.pie(
                        repartition_public,
                        names='Public',
                        values='Nombre',
                        hole=0.4,
                        color='Public',
                        color_discrete_map=color_mapping_public
                    )

                    # Mise en forme du graphique
                    fig_pie_public.update_layout(
                        width=300,
                        height=200,
                        title_text="",  # Pas de titre
                        legend=dict(
                            orientation="h",  # Orientation horizontale
                            yanchor="bottom",
                            y=-0.5,  # Positionner la légende sous le graphique
                            xanchor="center",
                            x=0.5  # Centrer la légende
                        ),
                        margin=dict(t=0, b=0)  # Réduire les marges
                    )

                    # Affichage du graphique dans Streamlit
                    st.plotly_chart(fig_pie_public)

                repartition_public_global(data_cleaned_impact_cp)


            with col2:


                # @st.cache_data
                # def repartition_par_type_global(df):
                #     """
                #     Affiche un graphique en barres empilées pour la répartition des types d'activités par public.

                #     Args:
                #         data_cleaned_impact_cp (pd.DataFrame): Le DataFrame contenant les données des activités, incluant les colonnes
                #                                             'Type', 'Public', et "Nombre d'enseignants impactés".

                #     Returns:
                #         None: Affiche directement le graphique dans Streamlit.
                #     """
                #     # Création du graphique en barres empilées
                #     fig_stacked_bar_degre = px.bar(
                #         df,
                #         x="Nombre d'enseignants impactés",
                #         y='Type',
                #         color='Public',
                #         title=None,
                #         color_discrete_map=color_mapping_public
                #     )

                #     # Mise en forme du graphique
                #     fig_stacked_bar_degre.update_layout(
                #         barmode='stack',
                #         showlegend=False,
                #         width=500,
                #         height=200,
                #         margin=dict(l=10, r=10, t=20, b=20)  # Marges réduites
                #     )
                #     fig_stacked_bar_degre.update_xaxes(title=None)  # Suppression du label de l'axe X
                #     fig_stacked_bar_degre.update_yaxes(title=None)  # Suppression du label de l'axe Y

                #     # Affichage du graphique dans Streamlit
                #     st.plotly_chart(fig_stacked_bar_degre)

                @st.cache_data
                def repartition_par_type_global(df):
                    """
                    Affiche un graphique en barres empilées avec le total des actions affiché à droite de chaque barre.

                    Args:
                        df (pd.DataFrame): DataFrame avec colonnes 'Type' et 'Public'.

                    Returns:
                        None
                    """
                    # Groupement des données pour compter le nombre d'actions
                    grouped = df.groupby(['Type', 'Public']).size().reset_index(name='Nombre d\'actions')

                    # Total par Type (pour affichage du total)
                    totals = grouped.groupby('Type')['Nombre d\'actions'].sum().reset_index()

                    # Création du graphique en barres empilées
                    fig = px.bar(
                        grouped,
                        x="Nombre d'actions",
                        y='Type',
                        color='Public',
                        orientation='h',
                        color_discrete_map=color_mapping_public
                    )

                    fig.update_layout(
                        barmode='stack',
                        showlegend=False,
                        width=500,
                        height=200,
                        margin=dict(l=10, r=10, t=20, b=20)
                    )

                    fig.update_xaxes(title=None)
                    fig.update_yaxes(title=None)

                    # Ajouter les annotations de total
                    for i, row in totals.iterrows():
                        fig.add_annotation(
                            x=row["Nombre d'actions"] + 2,  # un petit décalage pour lisibilité
                            y=row["Type"],
                            text=str(row["Nombre d'actions"]),
                            showarrow=False,
                            font=dict(color="black"),
                            xanchor="left",
                            yanchor="middle"
                        )

                    st.plotly_chart(fig)



                repartition_par_type_global(data_cleaned_impact_cp)



    # Section 2 :
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:

            @st.cache_data
            def impact_par_etablissement(df):
                """
                Affiche un graphique en barres pour le nombre total d'enseignants impactés par établissement.

                Args:
                    df (pd.DataFrame): Le DataFrame contenant les données des activités, incluant les colonnes
                                    'Établissement cible' et "Nombre d'enseignants impactés".

                Returns:
                    None: Affiche directement le graphique dans Streamlit.
                """
                # Préparation des données
                data_expanded = df.assign(
                    Établissement_cible=df['Établissement cible'].str.split(',')
                ).explode('Établissement_cible')  # Diviser les établissements multiples dans des lignes séparées
                data_expanded['Établissement_cible'] = data_expanded['Établissement_cible'].str.strip()  # Supprimer les espaces inutiles

                # Calcul du nombre total d'enseignants impactés par établissement
                impact_etablissement = (
                    data_expanded.groupby('Établissement_cible')['Nombre d\'enseignants impactés']
                    .sum()
                    .reset_index()
                    .sort_values(by='Nombre d\'enseignants impactés', ascending=False)  # Tri par ordre décroissant
                )

                # Création du graphique en barres
                fig= px.bar(
                    impact_etablissement,
                    x='Établissement_cible',
                    y='Nombre d\'enseignants impactés',
                    title="Nombre d'enseignants impactés par établissement",
                    color_discrete_sequence=px.colors.qualitative.T10 # Utiliser une palette cohérente
                )

                # Mise en forme du graphique
                fig.update_layout(
                    height=220,  # Même hauteur que les pie charts
                    margin=dict(t=20, b=20)  # Marges réduites pour un meilleur équilibre
                )
                fig.update_xaxes(title=None)  # Suppression du titre de l'axe X
                fig.update_yaxes(title=None)  # Suppression du titre de l'axe Y

                # Affichage dans Streamlit
                st.plotly_chart(fig)

            @st.cache_data
            def impact_par_etablissement_normalise(df):
                """
                Affiche un graphique en barres pour le nombre total d'enseignants impactés par établissement,
                normalisé par l'effectif total des enseignants de chaque établissement, et pondéré par la durée.

                Args:
                    df (pd.DataFrame): Le DataFrame contenant les données des activités, incluant les colonnes
                                    'Établissement cible', "Nombre d'enseignants impactés", 'Durée (en heure)', et 'Type'.

                Returns:
                    None: Affiche directement le graphique dans Streamlit.
                """
                # Dictionnaire des effectifs des établissements
                effectifs_etablissements = {
                    "Louis-Massignon": 316,
                    "Malraux": 162,
                    "Agadir": 103,
                    "Daudet": 70,
                    "Tanger": 66,
                    "Marrakech": 51,
                    "El Jadida": 50,
                    "Dakhla": 29,
                    "Laayoune": 26,
                    "Essaouira": 10
                }

                # Préparation des données
                data_expanded = df.assign(
                    Établissement_cible=df['Établissement cible'].str.split(',')
                ).explode('Établissement_cible')  # Diviser les établissements multiples dans des lignes séparées
                data_expanded['Établissement_cible'] = data_expanded['Établissement_cible'].str.strip()  # Supprimer les espaces inutiles

                # Calcul du nombre total d'enseignants impactés par établissement et par type, pondéré par la durée
                impact_etablissement = (
                    data_expanded.groupby(['Établissement_cible', 'Type'])  # Ajouter 'Type' au groupby
                    .apply(lambda x: (x['Nombre d\'enseignants impactés'] * x['Durée (en heure)']).sum())  # Pondération par durée
                    .reset_index(name='Impact pondéré')
                )

                # Ajout de l'effectif des enseignants à chaque établissement
                impact_etablissement['Effectif'] = impact_etablissement['Établissement_cible'].map(effectifs_etablissements)

                # Calcul du ratio "Impact pondéré" / "Effectif"
                impact_etablissement['Ratio impact/effectif'] = (
                    impact_etablissement['Impact pondéré'] / impact_etablissement['Effectif']
                )

                # Trier les établissements par ordre décroissant du ratio
                impact_etablissement = impact_etablissement.sort_values(by='Ratio impact/effectif', ascending=False)

                # Création du graphique en barres
                fig = px.bar(
                    impact_etablissement,
                    x='Établissement_cible',
                    y='Ratio impact/effectif',
                    color='Type',
                    title="Taux d'exposition aux CP par établissement et par enseignant (pondéré par durée)",
                    color_discrete_sequence=px.colors.qualitative.T10  # Utiliser une palette cohérente
                )

                # Mise en forme du graphique
                fig.update_layout(
                    height=250,  # Même hauteur que les pie charts
                    margin=dict(t=30, b=0)  # Marges réduites pour un meilleur équilibre
                )
                fig.update_xaxes(title=None)  # Suppression du titre de l'axe X
                fig.update_yaxes(title="Ratio impact/effectif")  # Ajout d'un titre pour l'axe Y

                # Affichage dans Streamlit
                st.plotly_chart(fig)


            impact_par_etablissement_normalise(data_cleaned_impact_cp)

        with col2:

            @st.cache_data
            def charge_travail(df):
                """
                Affiche un graphique de la charge de travail quotidienne avec une barre pour la durée en heures
                et une courbe de moyenne mobile sur 7 jours.

                Args:
                    df (pd.DataFrame): Le DataFrame contenant les données des missions avec les colonnes
                                    'Date', 'Durée (en heure)' et 'Nombre d\'enseignants impactés'.

                Returns:
                    None: Affiche directement le graphique dans Streamlit.
                """
                # Regrouper les données par date et calculer la somme des heures et des enseignants impactés
                tendance = df.groupby(pd.Grouper(key='Date')).agg({
                    'Durée (en heure)': 'sum',
                    'Nombre d\'enseignants impactés': 'sum'
                }).reset_index()

                # Trier par date
                tendance = tendance.sort_values(by='Date')

                # Calcul de la moyenne mobile sur la colonne 'Durée (en heure)' sur une fenêtre de 7 jours
                tendance['Moyenne_mobile'] = tendance['Durée (en heure)'].rolling(window=6).mean()

                # Création du graphique
                fig = px.bar(
                    tendance,
                    x='Date',
                    y='Durée (en heure)',
                    title="Nombre d'heures d'intervention par jour",
                    color_discrete_sequence=px.colors.qualitative.T10
                )
                fig.update_layout(
                    height=220,  # Même hauteur que les pie charts
                    margin=dict(t=20, b=20)
                )

                # Suppression des titres des axes
                fig.update_xaxes(title=None, tickformat='%d/%m/%Y')
                fig.update_yaxes(title="Durée (en heure)")

                # Ajout de la ligne de moyenne mobile
                fig.add_scatter(
                    x=tendance['Date'],
                    y=tendance['Moyenne_mobile'],
                    mode='lines',
                    name='Moyenne mobile (7 jours)',
                    showlegend=False,
                    fill='tozeroy',
                    line_shape='spline',
                    line=dict(color=px.colors.qualitative.T10[1], width=2)
                )

                # Affichage du graphique dans Streamlit
                st.plotly_chart(fig)

            charge_travail(data_cleaned_impact_cp)




with tab1:


    @st.cache_data
    def nettoyer_data_avis_de_mission(file_id, gid, verbose=False, colonnes_a_supprimer=None, colonnes_essentielles=None, nettoyer_texte=True):
        if colonnes_a_supprimer is None:
            colonnes_a_supprimer = ['N° D\'intervention', 'N°']
        if colonnes_essentielles is None:
            colonnes_essentielles = ['Nom / Prénom', 'Date d\'intervention']

        # Charger la feuille
        try:
            url = f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=csv&gid={gid}"
            data_avis_de_mission = pd.read_csv(url)
            print(data_avis_de_mission.columns)
        except Exception as e:
            print(f"Erreur lors du chargement des données : {e}")
            return None

        if verbose:
            print(f"Données chargées : {data_avis_de_mission.shape}")

        # Conversion des dates
        data_avis_de_mission["Date d'intervention"] = pd.to_datetime(
            data_avis_de_mission["Date d'intervention"], format='%d/%m/%Y', errors='coerce'
        ).dt.date

        # Supprimer les colonnes inutiles
        data_avis_de_mission = data_avis_de_mission.drop(columns=colonnes_a_supprimer, errors='ignore')

        # Supprimer les lignes où des colonnes essentielles ont des valeurs manquantes
        data_avis_de_mission = data_avis_de_mission.dropna(subset=colonnes_essentielles)

        # Conversion des colonnes numériques
        for col in ['Nombre de jour', 'Année scolaire 2024/2025']:
            if col in data_avis_de_mission.columns:
                data_avis_de_mission[col] = data_avis_de_mission[col].fillna(0).astype(int)

        # Renommer les colonnes
        nouveaux_noms = {
            'Nom / Prénom': 'Nom',
            'Discipline': 'Discipline',
            'Lieu d\'intervention': 'Lieu',
            "Date d'intervention": 'Date',
            'Nombre de jours': 'nb_jours',
            'Année scolaire 2024/2025': 'AnneeScolaire',
            'Mission': 'Mission',
            'Objet de la mission': 'Objet',
            'Situation': 'Situation'
        }
        data_avis_de_mission = data_avis_de_mission.rename(columns=nouveaux_noms)

        # Nettoyage des colonnes textuelles
        if nettoyer_texte:
            for col in data_avis_de_mission.select_dtypes(include=['object']).columns:
                data_avis_de_mission[col] = (
                    data_avis_de_mission[col]
                    .astype(str)
                    .str.strip()
                    .replace('', pd.NA)
                    .str.lower()
                )

        if verbose:
            print(f"Données nettoyées : {data_avis_de_mission.shape}")

        return data_avis_de_mission

    df_avis_de_mission=nettoyer_data_avis_de_mission(file_id_avis_de_mission, gid['avis_de_mission'],verbose=False, colonnes_a_supprimer=None, colonnes_essentielles=None, nettoyer_texte=True)

    with st.container(border=True):

        # Nombre total de missions réalisées

        def afficher_total_missions(df):
            """
            Affiche le nombre total de missions réalisées dans un conteneur Streamlit.

            Args:
                df (pd.DataFrame): Le DataFrame contenant les données des missions.

            Returns:
                None: Affiche directement la métrique dans Streamlit.
            """
            total_missions = df.shape[0]
            return st.metric(label="Nombre total de missions", value=total_missions)

        # Durée moyenne des missions

        def afficher_duree_moyenne_missions(df):
            """
            Affiche la durée moyenne des missions réalisées dans un conteneur Streamlit.

            Args:
                df (pd.DataFrame): Le DataFrame contenant les données des missions.

            Returns:
                None: Affiche directement la métrique dans Streamlit.
            """
            duree_moyenne = df['nb_jours'].mean()
            return st.metric(label="Durée moyenne des missions (jours)", value=f"{duree_moyenne:.2f}")

        # Visualisation des missions par CP


        def visualiser_missions_par_cp_streamlit(df):
            """
            Affiche un bar chart du nombre total de missions réalisées par CP dans Streamlit.

            Args:
                df (pd.DataFrame): Le DataFrame contenant les données des missions.

            Returns:
                None: Affiche directement le graphique dans Streamlit.
            """
            # Calcul du nombre de missions par CP
            df_missions_cp = df['Nom'].value_counts().reset_index()
            df_missions_cp.columns = ['CP', 'Nombre de missions']
            df_missions_cp = df_missions_cp.sort_values(by='Nombre de missions', ascending=False)


            # Création du graphique avec Plotly
            fig = px.bar(
                df_missions_cp,
                # x='Nombre de missions',
                # y='CP',
                x='CP',
                y='Nombre de missions',
                text='Nombre de missions',
                color_discrete_sequence=px.colors.qualitative.T10
            )
            # Mise en forme du graphique
            fig.update_traces(textposition='outside')
            fig.update_layout(showlegend=False,
                                width=100,
                                height=300,
                                legend=dict(orientation="h", yanchor="top", y=-2, xanchor="center", x=0.5),
                                xaxis_title="",
                                yaxis_title="Nombre de mission",
                                yaxis=dict(range=[0, df_missions_cp['Nombre de missions'].max() + 5])  # Ajuste l'échelle
    )

            # Affichage dans Streamlit

            return st.plotly_chart(fig, use_container_width=True)


        # Visualisation de la répartition par degré


        def visualiser_repartition_par_degre_streamlit(df):
            """
            Affiche un pie chart de la répartition des missions par degré (1/2) dans Streamlit.

            Args:
                df (pd.DataFrame): Le DataFrame contenant les données des missions.

            Returns:
                None: Affiche directement le graphique dans Streamlit.
            """
            # Calcul de la répartition par degré
            repartition_degre = df['Mission'].value_counts().reset_index()
            repartition_degre.columns = ['Degré', 'Nombre de missions']

            # Mapping des valeurs pour afficher Degré 1 / Degré 2
            repartition_degre['Degré'] = repartition_degre['Degré'].map({'cp1d': 'Degré 1', 'cp2d': 'Degré 2'})

            # Création du graphique avec Plotly
            fig = px.pie(
                repartition_degre,
                names='Degré',
                values='Nombre de missions',
                title="Degré 1 vs Degré 2",
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.T10
            )

            # Mise en forme du graphique
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(
                title=dict(x=0.3),
                width=300,              # Largeur du graphique
                height=300,
                showlegend=False,
                # legend=dict(orientation="h",
                #             yanchor="bottom",
                #             y=-0.2,
                #             xanchor="center",
                #             x=0.5),
                margin=dict(l=20, r=20, t=30, b=20)
            )

            # Affichage dans Streamlit

            return st.plotly_chart(fig, use_container_width=True)


        def nb_missions_par_etablissement(df):
            """
            Affiche un bar chart du nombre total de missions réalisées par établissement.

            Args:
                df (pd.DataFrame): Le DataFrame contenant les données des missions.

            Returns:
                None: Affiche directement le graphique avec Plotly.
            """
            # Calcul du nombre de missions par établissement
            missions_par_etablissement = df['Lieu'].value_counts().reset_index()
            missions_par_etablissement.columns = ['Établissement', 'Nombre de missions']

            # Trier les établissements par nombre de missions (ordre décroissant)
            missions_par_etablissement = missions_par_etablissement.sort_values(by='Nombre de missions', ascending=False)

            # Création du graphique avec Plotly
            fig = px.bar(
                missions_par_etablissement,
                x='Établissement',
                y='Nombre de missions',
                text='Nombre de missions',
                color_discrete_sequence=[px.colors.qualitative.T10[3]] # Palette de couleurs
            )

            # Mise en forme du graphique
            fig.update_traces(textposition='outside', texttemplate='%{text}')
            fig.update_layout(
                xaxis=dict(title=""),
                width=200,              # Largeur du graphique
                height=250,
                yaxis=dict(
                    title="Nombre de missions",  # Titre de l'axe
                    range=[0, missions_par_etablissement['Nombre de missions'].max() + 10]  # Plage de l'axe y
                ),
            )

            # Affichage du graphique
            st.plotly_chart(fig, use_container_width=True)

        @st.cache_data
        def nb_missions_par_etablissement_par_eleve(df):
            """
            Affiche un bar chart du ratio missions/élèves pour chaque établissement.

            Args:
                df (pd.DataFrame): Le DataFrame contenant les données des missions,
                                incluant une colonne 'Nombre d'élèves'.

            Returns:
                None: Affiche directement le graphique avec Plotly.
            """
            # Calcul du nombre total de missions par établissement
            missions_par_etablissement_par_eleve = df['Lieu'].value_counts().reset_index()
            missions_par_etablissement_par_eleve.columns = ['Établissement', 'Nombre de missions']

            # Ajout du nombre d'élèves à partir des données préexistantes
            nombre_eleves = {
                'agadir': 1400, 'lfiad': 884, 'lfilm': 4319, 'tanger': 882,
                'dakhla': 263, 'lfijc': 601, 'essaouira': 60, 'laayoune': 260,
                'gs majorelle': 603, 'lfiam': 2014, 'oujda': 336
            }
            missions_par_etablissement_par_eleve['Nombre d\'élèves'] = missions_par_etablissement_par_eleve['Établissement'].map(nombre_eleves)

            # Calcul du ratio missions/élèves
            missions_par_etablissement_par_eleve['Ratio missions/élèves'] = (
                missions_par_etablissement_par_eleve['Nombre de missions'] / missions_par_etablissement_par_eleve['Nombre d\'élèves']
            )
            # Trier par ordre décroissant du ratio missions/élèves
            missions_par_etablissement_par_eleve = missions_par_etablissement_par_eleve.sort_values(by='Ratio missions/élèves', ascending=False)


            # Création du graphique avec Plotly
            fig = px.bar(
                missions_par_etablissement_par_eleve,
                x='Établissement',
                y='Ratio missions/élèves',
                text='Ratio missions/élèves',
                color_discrete_sequence=[px.colors.qualitative.T10[2]]  # Palette de couleurs
            )

            # Mise en forme du graphique
            fig.update_traces(textposition='outside', texttemplate='%{text:.2f}')
            fig.update_layout(
                xaxis=dict(title=""),
                width=200,              # Largeur du graphique
                height=250,
                yaxis=dict(
                    title="Nombre de missions par élève",  # Titre de l'axe
                    range=[0,missions_par_etablissement_par_eleve['Ratio missions/élèves'].max() + 0.01]  # Plage de l'axe y
                ),
            )

            # Affichage du graphique
            st.plotly_chart(fig, use_container_width=True)



        col1, col2= st.columns([1,2])
        with col1:
            st.subheader("Activité Globable")
            afficher_total_missions(df_avis_de_mission)
            afficher_duree_moyenne_missions(df_avis_de_mission)
            st.write("")
            visualiser_repartition_par_degre_streamlit(df_avis_de_mission)

        with col2:
                    # Utilisation de st.toggle

            if st.toggle("Afficher le nombre total de missions par établissement et par élève", value=False):
                nb_missions_par_etablissement_par_eleve(df_avis_de_mission)

            else:
                nb_missions_par_etablissement(df_avis_de_mission)

            visualiser_missions_par_cp_streamlit(df_avis_de_mission)





    with st.container(border=True):

        @st.cache_data
        def repartition_par_objet_et_degre(df, etablissement):
            """
            Affiche un stacked bar chart des missions par objets et par degré pour un établissement donné.

            Args:
                df (pd.DataFrame): Le DataFrame contenant les données des missions.
                etablissement (str): Le nom de l'établissement.

            Returns:
                None: Affiche directement le graphique avec Plotly.
            """
            df_etab = df[df['Lieu'] == etablissement].copy()  # Création d'une copie explicite
            df_etab['Degré'] = df_etab['Mission'].apply(lambda x: "Degré 1" if "cp1" in x.lower() else "Degré 2")

            repartition = df_etab.groupby(['Objet', 'Degré'])['Nom'].count().reset_index()
            repartition.columns = ['Objet', 'Degré', 'Nombre de missions']

            fig = px.bar(
                repartition,
                x='Objet',
                y='Nombre de missions',
                color='Degré',
                barmode='stack',
                title="Themes des missions",
                text='Nombre de missions',
                color_discrete_sequence=px.colors.qualitative.T10
            )
            fig.update_traces(textposition='outside')
            fig.update_layout(
                width=400,              # Largeur du graphique
                height=250,
                xaxis_title="",
                yaxis_title="Nombre de missions",
                legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1, title=None),
                xaxis=dict(tickangle=25),
                margin=dict(l=20, r=20, t=40, b=0)
            )
            st.plotly_chart(fig)

        @st.cache_data
        def repartition_par_degre_etablissement(df, etablissement):
            """
            Affiche un pie chart de la répartition des missions par degré pour un établissement donné.

            Args:
                df (pd.DataFrame): Le DataFrame contenant les données des missions.
                etablissement (str): Le nom de l'établissement.

            Returns:
                None: Affiche directement le graphique avec Plotly.
            """
            df_etab = df[df['Lieu'] == etablissement].copy()  # Création d'une copie explicite
            df_etab['Degré'] = df_etab['Mission'].apply(lambda x: "Degré 1" if "cp1" in x.lower() else "Degré 2")

            repartition = df_etab['Degré'].value_counts().reset_index()
            repartition.columns = ['Degré', 'Nombre de missions']

            fig = px.pie(
                repartition,
                names='Degré',
                values='Nombre de missions',
                hole=0.4,
                title="Degré 1 vs Degré 2",
                color_discrete_sequence=px.colors.qualitative.T10
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(
                title=dict(x=0.2),
                showlegend=False,
                width=220,              # Largeur du graphique
                height=220,
                margin=dict(l=20, r=20, t=30, b=0)
            )
            st.plotly_chart(fig)

        @st.cache_data
        def repartition_degre2_par_discipline(df, etablissement):
            """
            Affiche un pie chart de la répartition des missions de degré 2 par discipline pour un établissement donné.

            Args:
                df (pd.DataFrame): Le DataFrame contenant les données des missions.
                etablissement (str): Le nom de l'établissement.

            Returns:
                None: Affiche directement le graphique avec Plotly.
            """
            df_etab = df[df['Lieu'] == etablissement].copy()  # Création d'une copie explicite
            df_etab_degre2 = df_etab[df_etab['Mission']=="cp2d"].copy()  # Création d'une copie explicite\

            repartition = df_etab_degre2['Discipline'].value_counts().reset_index()
            repartition.columns = ['Discipline', 'Nombre de missions']

            fig = px.pie(
                repartition,
                names='Discipline',
                values='Nombre de missions',
                hole=0.4,
                title="Degré 2 : matières",
                color_discrete_sequence=px.colors.qualitative.T10

            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(
                title=dict(x=0.15),
                width=220,              # Largeur du graphique
                height=220,
                # legend=dict(orientation="h", yanchor="top", y=0, xanchor="center", x=0.5),
                showlegend=False,
                margin=dict(l=20, r=20, t=30, b=0)
            )


            st.plotly_chart(fig)

        @st.cache_data
        def somme_jours_formation_par_etablissement(df, etablissement):
            """
            Calcule la somme des jours de formation pour un établissement donné.

            Args:
                df (pd.DataFrame): Le DataFrame contenant les données des missions.
                etablissement (str): Le nom de l'établissement sélectionné.

            Returns:
                int: Somme des jours de formation pour l'établissement.
            """
            # Filtrer le DataFrame pour l'établissement sélectionné
            df_filtered = df[df['Lieu'] == etablissement]

            # Calculer la somme des jours de formation
            somme_jours = df_filtered['nb_jours'].sum()

            return somme_jours


        col1,col2,col3,col4=st.columns(4)
        with col1:
            st.subheader("Activité par Établissement")
            etablissements = sorted(df_avis_de_mission['Lieu'].unique().tolist())
            # Afficher le sélecteur pour choisir un établissement
            selected_etablissement = st.selectbox(
                "Sélectionnez un établissement :",  # Label du sélecteur
                options=etablissements  # Options extraites du DataFrame
            )
            somme_jours = somme_jours_formation_par_etablissement(df_avis_de_mission, selected_etablissement)
            st.metric(label=f"Total des jours de formation pour {selected_etablissement}", value=somme_jours)
        with col2:
            repartition_par_degre_etablissement(df_avis_de_mission,selected_etablissement)
        with col3:
            repartition_degre2_par_discipline(df_avis_de_mission,selected_etablissement)
        with col4:
            repartition_par_objet_et_degre(df_avis_de_mission,selected_etablissement)


    with st.container(border=True):

        def total_missions_cp(df, nom_cp):
            """
            Calcule le nombre total de missions réalisées pour un CP donné.

            Args:
                df (pd.DataFrame): Le DataFrame contenant les données des missions.
                nom_cp (str): Le nom du CP.

            Returns:
                int: Nombre total de missions réalisées pour le CP.
            """
            return df[df['Nom'] == nom_cp].shape[0]

        def repartition_par_etablissement_cp(df, nom_cp):
            """
            Affiche un bar chart de la répartition des missions par établissement pour un CP donné.

            Args:
                df (pd.DataFrame): Le DataFrame contenant les données des missions.
                nom_cp (str): Le nom du CP.

            Returns:
                None: Affiche directement le graphique avec Plotly.
            """
            df_cp = df[df['Nom'] == nom_cp]
            missions_par_etablissement = df_cp['Lieu'].value_counts().reset_index()
            missions_par_etablissement.columns = ['Établissement', 'Nombre de missions']
            missions_par_etablissement=missions_par_etablissement.sort_values(by='Nombre de missions', ascending=True)

            fig = px.bar(
                missions_par_etablissement,
                x='Nombre de missions',
                y='Établissement',
                text='Nombre de missions',
                orientation='h',
                color_discrete_sequence=px.colors.qualitative.T10
            )
            fig.update_traces(textposition='outside')
            fig.update_layout(
                height=300,
                xaxis_title="Nombre de missions",
                yaxis_title="")

            st.plotly_chart(fig)

        def repartition_par_objet_cp(df, nom_cp):
            """
            Affiche un pie chart de la répartition des missions par objet pour un CP donné.

            Args:
                df (pd.DataFrame): Le DataFrame contenant les données des missions.
                nom_cp (str): Le nom du CP.

            Returns:
                None: Affiche directement le graphique avec Plotly.
            """
            df_cp = df[df['Nom'] == nom_cp]
            missions_par_objet = df_cp['Objet'].value_counts().reset_index()
            missions_par_objet.columns = ['Objet', 'Nombre de missions']

            fig = px.pie(
                missions_par_objet,
                names='Objet',
                values='Nombre de missions',
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.T10
            )
            fig.update_traces(
                textposition='inside',
                textinfo='label+percent'  # Affiche les noms et les pourcentage
                )
            fig.update_layout(
                width=250,              # Largeur du graphique
                height=250,
                # legend=dict(orientation="h", yanchor="top", y=0, xanchor="center", x=0.5),
                showlegend=False,
                margin=dict(l=20, r=20, t=20, b=20)
                )
            st.plotly_chart(fig)


        col1,col2,col3=st.columns([1,2,1])
        with col1:
            st.subheader("Activité par Conseiller Pédagogique")
            # Extraire les lieux uniques depuis la colonne 'Lieu' du DataFrame
            noms_cp = sorted(df_avis_de_mission['Nom'].unique().tolist())
            # Afficher le sélecteur pour choisir un établissement
            selected_name= st.selectbox(
                "Sélectionnez un nom :",  # Label du sélecteur
                options=noms_cp  # Options extraites du DataFrame
            )
            st.metric(label="Nombre de mission", value=total_missions_cp(df_avis_de_mission, selected_name))

        with col2:
            repartition_par_etablissement_cp(df_avis_de_mission, selected_name)

        with col3:
            repartition_par_objet_cp(df_avis_de_mission, selected_name)
