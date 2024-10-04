import streamlit as st
import pandas as pd
import plotly.express as px

# Charger les données depuis Google Sheets
sheet_id = "1_0osMjru69w5rYtekqHP0KAEmxaFhn0AW02x3DtP9a4"
sheet_name = "Feuille1"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

# Lire les données
data = pd.read_csv(url)

# Nettoyer les données
def nettoyer_donnees(data):
    colonnes_a_supprimer = ['Thèmes travaillés', 'Unnamed: 11', 'Unnamed: 12']
    data = data.drop(columns=colonnes_a_supprimer, errors='ignore')
    data['Durée (en heure)'] = pd.to_numeric(data['Durée (en heure)'], errors='coerce')
    data['Nombre d\'enseignants impactés'] = pd.to_numeric(data['Nombre d\'enseignants impactés'], errors='coerce')
    data['Efficacité perçue (1 : très faible ; 5 très haute)'] = pd.to_numeric(data['Efficacité perçue (1 : très faible ; 5 très haute)'], errors='coerce')
    data.rename(columns={'Efficacité perçue (1 : très faible ; 5 très haute)': 'Efficacité'}, inplace=True)
    data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
    data['Durée (en heure)'].fillna(0, inplace=True)
    data['Nombre d\'enseignants impactés'].fillna(0, inplace=True)
    data['Efficacité'].fillna(0, inplace=True)
    return data

data_cleaned = nettoyer_donnees(data)

# Calculer les indicateurs
total_interventions = len(data_cleaned)
total_enseignants = data_cleaned['Nombre d\'enseignants impactés'].sum()
duree_totale = data_cleaned['Durée (en heure)'].sum()
efficacite_moyenne_val = data_cleaned['Efficacité'].mean()

# Mise en page du tableau de bord



# # Configuration de la page
# st.set_page_config(
#     page_title="Dashboard Impact des CP",
#     layout="wide"
# )

# # Titre principal
# st.title("Impact des CP sur les enseignants")

# # Indicateurs principaux
# col1, col2, col3, col4 = st.columns(4)
# with col1:
#     st.metric(label="Total Interventions", value=total_interventions)
# with col2:
#     st.metric(label="Total Enseignants Impactés", value=total_enseignants)
# with col3:
#     st.metric(label="Durée Totale (en heure)", value=f"{duree_totale:.1f}")
# with col4:
#     st.metric(label="Efficacité Moyenne", value=f"{efficacite_moyenne_val:.2f}")

# # Section 1 : Types de formations (Pie chart à gauche) et Tendance temporelle (Bar chart à droite)
# st.subheader("Visualisations des Interventions")
# col1, col2 = st.columns(2)

# with col1:
#     repartition_type = data_cleaned['Type'].value_counts().reset_index()
#     repartition_type.columns = ['Type de Formation', 'Nombre']

#     fig_type = px.pie(repartition_type, names='Type de Formation', values='Nombre',
#                       title='Types de Formations',
#                       color_discrete_sequence=px.colors.sequential.Blues)
#     fig_type.update_layout(height=400, width=400, legend=dict(orientation="h", yanchor="bottom", y=-0.3))
#     st.plotly_chart(fig_type)

# with col2:
#     tendance = data_cleaned.groupby('Date').agg({'Durée (en heure)': 'sum'}).reset_index().dropna()
#     fig_tendance = px.bar(tendance, x='Date', y='Durée (en heure)', title="Tendance des Heures de Formation",
#                           color_discrete_sequence=px.colors.sequential.Blues)
#     st.plotly_chart(fig_tendance)

# # Section 2 : Enseignants impactés (Bar chart à gauche) et Formats de formation (Pie chart à droite)
# col1, col2 = st.columns(2)

# with col1:
#     data_expanded = data_cleaned.assign(Établissement_cible=data_cleaned['Établissement cible'].str.split(',')).explode('Établissement_cible')
#     data_expanded['Établissement_cible'] = data_expanded['Établissement_cible'].str.strip()
#     impact_etablissement = data_expanded.groupby('Établissement_cible')['Nombre d\'enseignants impactés'].sum().reset_index()

#     fig_impact = px.bar(impact_etablissement, x='Nombre d\'enseignants impactés', y='Établissement_cible', orientation='h',
#                         title="Enseignants par Établissement",
#                         color_discrete_sequence=px.colors.sequential.Blues)
#     st.plotly_chart(fig_impact)

# with col2:
#     repartition_format = data_cleaned['Format'].value_counts().reset_index()
#     repartition_format.columns = ['Format', 'Nombre']

#     fig_format = px.pie(repartition_format, names='Format', values='Nombre',
#                         title='Formats de Formation',
#                         color_discrete_sequence=px.colors.sequential.Blues)
#     fig_format.update_layout(height=400, width=400, legend=dict(orientation="h", yanchor="bottom", y=-0.3))
#     st.plotly_chart(fig_format)


# Configuration de la page
st.set_page_config(
    page_title="Dashboard Impact des CP",
    layout="wide"
)

# Titre principal
st.title("Impact des CP sur les enseignants")

# Indicateurs principaux
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Total Interventions", value=total_interventions)
with col2:
    st.metric(label="Total Enseignants Impactés", value=total_enseignants)
with col3:
    st.metric(label="Durée Totale (en heure)", value=f"{duree_totale:.1f}")
with col4:
    st.metric(label="Efficacité Moyenne", value=f"{efficacite_moyenne_val:.2f}")

# Section 1 : Types de formations (Pie chart à gauche) et Tendance temporelle (Bar chart à droite)

col1, col2 = st.columns(2)

with col1:
    repartition_type = data_cleaned['Type'].value_counts().reset_index()
    repartition_type.columns = ['Type de Formation', 'Nombre']

    fig_type = px.pie(repartition_type, names='Type de Formation', values='Nombre',
                      title='Types de Formations',
                      color_discrete_sequence=px.colors.qualitative.Plotly)  # Meilleure palette de couleurs
    fig_type.update_layout(height=400, width=400, legend=dict(orientation="h", yanchor="bottom", y=-0.3))
    st.plotly_chart(fig_type)

with col2:
    tendance = data_cleaned.groupby('Date').agg({'Durée (en heure)': 'sum'}).reset_index().dropna()
    fig_tendance = px.bar(tendance, x='Date', y='Durée (en heure)', title="Tendance des Heures de Formation",
                          color_discrete_sequence=px.colors.qualitative.Plotly)  # Utiliser la même palette
    st.plotly_chart(fig_tendance)

# Section 2 : Enseignants impactés (Bar chart à gauche) et Formats de formation (Pie chart à droite)
col1, col2 = st.columns(2)

with col1:
    data_expanded = data_cleaned.assign(Établissement_cible=data_cleaned['Établissement cible'].str.split(',')).explode('Établissement_cible')
    data_expanded['Établissement_cible'] = data_expanded['Établissement_cible'].str.strip()
    impact_etablissement = data_expanded.groupby('Établissement_cible')['Nombre d\'enseignants impactés'].sum().reset_index()

    fig_impact = px.bar(impact_etablissement, x='Nombre d\'enseignants impactés', y='Établissement_cible', orientation='h',
                        title="Enseignants par Établissement",
                        color_discrete_sequence=px.colors.qualitative.Plotly)  # Palette contrastée
    st.plotly_chart(fig_impact)

with col2:
    repartition_format = data_cleaned['Format'].value_counts().reset_index()
    repartition_format.columns = ['Format', 'Nombre']

    fig_format = px.pie(repartition_format, names='Format', values='Nombre',
                        title='Formats de Formation',
                        color_discrete_sequence=px.colors.qualitative.Plotly)  # Utiliser la palette Plotly
    fig_format.update_layout(height=400, width=400, legend=dict(orientation="h", yanchor="bottom", y=-0.3))
    st.plotly_chart(fig_format)
