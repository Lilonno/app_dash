#TP Noté - Site dash cours
import dash
from dash import dcc, html, Input, Output, callback
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import pandas as pd
from dash import dash_table
import numpy as np

# Initialisation de l'application Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Lecture des données
data = pd.read_csv("data.csv")


 
print("Voici le lien, pour mon tableau de bord, veuillez cliquer sur le lien: ")


#Figure1
#Calcul de l'indicateur de la figure 1
data['Transaction_Date'] = pd.to_datetime(data['Transaction_Date'])
data['Month'] = data['Transaction_Date'].dt.month

data['Total_Amount'] = data['Quantity'] * data['Avg_Price']
data['Total_Amount'] = data['Total_Amount'] * (1 - data['Discount_pct'] / 100)

chiffre_affaires_par_mois = data.groupby('Month')['Total_Amount'].sum()

#Figure 1 mise en page 
def chiffre_affaires_par_mois(df) :
    fig1 = go.Figure()
    
    fig1.add_trace(go.Indicator(
    mode="number+delta",
    value=chiffre_affaires_par_mois[12],
    delta={'reference': chiffre_affaires_par_mois[11]}
))
    fig1.update_layout(
    margin=dict(l=0, t=0, r=0, b=0),
    height=100, 
    width=150,
)

#Figure 2 
#Calcul de la fgure 2 
data['Transaction_Date'] = pd.to_datetime(data['Transaction_Date'])

data['Month'] = data['Transaction_Date'].dt.month

ventes_par_mois = data.groupby('Month').size()
ventes_par_mois = ventes_par_mois.apply(lambda x: int(np.ceil(x / 10.0)) * 10)


#Mise en page de la figure 2 
def ventes_par_mois(df):
    fig2 = go.Figure()
    
    fig2.add_trace(go.Indicator(
    mode="number+delta",
    value=ventes_par_mois[12],
    delta={'reference': ventes_par_mois[11]},
    title='December',
))
    fig2.update_layout(
    margin=dict(l=0, t=0, r=0, b=0),
    height=100, 
    width=150,
)

#Figure 3 : Fréquence des 10 meilleurs ventes
#Calcul de la figure 3 
data['Frequence'] = data['Avg_Price'] * (1 - data["Discount_pct"] / 100)

sales_by_category_gender = data.groupby(['Product_Category', 'Gender'])['Frequence'].mean().reset_index()

sales_by_category_gender_sorted = sales_by_category_gender.groupby(['Product_Category', 'Gender']).mean().reset_index()
sales_by_category_gender_sorted = sales_by_category_gender_sorted.sort_values(by=['Gender', 'Frequence'], ascending=[True, False])

top_10_categories_male = sales_by_category_gender_sorted[sales_by_category_gender_sorted['Gender'] == 'M'].head(10)
top_10_categories_female = sales_by_category_gender_sorted[sales_by_category_gender_sorted['Gender'] == 'F'].head(10)


#Mise en page de la figure 3
def frequence_ventes_best(df) :
    fig3 = go.Figure()
    
    fig3.add_trace(go.Bar(
    y=top_10_categories_female['Product_Category'][::-1],
    x=top_10_categories_female['Frequence'][::-1],
    orientation='h',
    name='F',
    marker=dict(color='blue')
))
    fig3.add_trace(go.Bar(
    y=top_10_categories_male['Product_Category'][::-1],  
    x=top_10_categories_male['Frequence'][::-1],  
    orientation='h',  
    name='M',
    marker=dict(color='red')
))
    fig3.update_layout(
    title='Fréquence des 10 meilleures ventes',
    xaxis_title='Total vente',
    yaxis_title='Catégorie de produit',
    legend_title="Sexe",
    height=150, 
    width=500, 
    margin = dict(r=0,l=0,t=0, b=0)
)

#Figure4  : Evolution des chiffres d'affaires par semaine 

#Calcul de la figure 4 
data['Transaction_Date'] = pd.to_datetime(data['Transaction_Date'])

data['Year_Week'] = data['Transaction_Date'].dt.strftime('%Y-%U')

data['Total_Amount'] = data['Quantity'] * data['Avg_Price']
data['Total_Amount'] = data['Total_Amount'] * (1 - data['Discount_pct'] / 100)

chiffre_affaires_par_semaine = data.groupby('Year_Week')['Total_Amount'].sum(numeric_only=True).reset_index()
chiffre_affaires_par_semaine2 = data.resample('W-Mon', on='Transaction_Date').sum()


# on va convertir la variable  'Transaction_Date' en datetime sinon le tableau ne se fait pas
data['Transaction_Date'] = pd.to_datetime(data['Transaction_Date'])

#mise en forme de la figure 4

def evolution_chiffre_affaire(df) :
    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(x=df.resample('W-Mon',on = 'Transaction_Date').sum().index,
                             y=chiffre_affaires_par_semaine['Total_Amount'],
                             mode="lines"))

    fig4.update_layout(title="Évolution du chiffre d'affaires par semaine",
                      xaxis_title="Semaine",
                      yaxis_title="Chiffre d'affaires",
                       height=400, 
                       width=650)



# Table des 100 dernières ventes
#Calcul du tableau
data = data.sort_values(by='Transaction_Date', ascending=False)
data['Date'] = pd.to_datetime(data['Date'])
data['Date'] = data['Date'].dt.strftime('%Y-%m-%d')

def table_data(df) :
    columns_to_display = ['Date', 'Gender', 'Location', 'Product_Category', 'Quantity', 'Avg_Price', 'Discount_pct']
    df_last_100_sales = df.sort_values(by='Transaction_Date', ascending=False).head(100)
    table_last_100_sales = html.Div([
        html.H3("Table des 100 dernières ventes", style={"font-size": "16px"}), 
        dash_table.DataTable(
            id='fig-5',
            columns=[{"name": i, "id": i} for i in columns_to_display],
            data=df_last_100_sales[columns_to_display].to_dict('records'),
            page_size=10,
            style_table={'overflowX': 'scroll'}
        )
    ])
    return table_last_100_sales



# mise en page de l'application Dash
app.layout = dbc.Container([
    # Bandeau supérieur
    dbc.Row([
        dbc.Col(html.Div("ONNO Lilou - Tableau de bord des ventes", style={
            "font-size": "24px", 
            "font-weight": "bold", 
            "color": "#ffffff",
            "padding": "10px"
        }), width=8),
        dbc.Col(
            dcc.Dropdown(
                id="location-id",
                options=[{'label': v, 'value': v} for v in data["Location"].dropna().unique()],
                multi=True,
                searchable=True,
                placeholder='Choisissez une ou plusieurs zones géographiques',
                style={"color": "#000"}
            ), 
            width=4
        ),
    ], style={
        "backgroundColor": "#3f6791", 
        "padding": "10px", 
        "margin-bottom": "15px",
        "border-radius": "8px"
    }),

    # Corps principal
    dbc.Row([
        # Colonne gauche : chiffres + graphique barres
        dbc.Col([
            dbc.Row([
                dbc.Col(dcc.Graph(id="fig-1", config={'displayModeBar': False}), width=6),
                dbc.Col(dcc.Graph(id="fig-2", config={'displayModeBar': False}), width=6),
            ], style={"padding": "10px"}),

            dbc.Row([
                dbc.Col(dcc.Graph(id="fig-3", config={'displayModeBar': False}), width=12),
            ], style={"padding": "10px"}),
        ], width=6, style={"background-color": "#ffffff", "padding": "10px", "border-right": "1px solid #eaeaea"}),

        # Colonne droite : graphique courbe + tableau
        dbc.Col([
            dbc.Row([
                dbc.Col(dcc.Graph(id="fig-4", config={'displayModeBar': False}), width=12),
            ], style={"padding": "10px"}),

            dbc.Row([
                dbc.Col([
                    html.Div("Table des 100 dernières ventes", style={
                        "font-size": "16px", "font-weight": "bold", "margin-bottom": "10px"
                    }),
                    dash_table.DataTable(
                        id='fig-5',
                        page_size=10,
                        style_table={'overflowX': 'scroll'},
                        style_cell={"textAlign": "left", "padding": "5px"},
                        style_header={"backgroundColor": "#f1f1f1", "fontWeight": "bold"}
                    )
                ], width=12),
            ], style={"padding": "10px"})
        ], width=6, style={"background-color": "#ffffff", "padding": "10px"})
    ])
], fluid=True, style={"background-color": "#f0f3f6"})

#CALL BACK


#app.callback figure 1
@app.callback(
    Output('fig-1', 'figure'),
    [Input('location-id', 'value')]
)
def update_chiffre_affaires_par_mois(locations):
    data_tmp = data[data['Location'].isin(locations)] if locations else data
    
    chiffre_affaires_par_mois = data_tmp.groupby('Month')['Total_Amount'].sum()

    fig1 = go.Figure()

    fig1.add_trace(go.Indicator(
        mode="number+delta",
        value=chiffre_affaires_par_mois[12],
        delta={'reference': chiffre_affaires_par_mois[11]}
    ))

    fig1.update_layout(
        margin=dict(l=0, t=0, r=0, b=0),
        height=100, 
        width=150,
    )

    return fig1



#app.callback figure 2
@app.callback(
    Output('fig-2', 'figure'),
    [Input('location-id', 'value')]
)
def update_ventes_par_mois(locations):
    data_tmp = data[data['Location'].isin(locations)] if locations else data
    
    ventes_par_mois = data_tmp.groupby('Month').size()
    ventes_par_mois = ventes_par_mois.apply(lambda x: int(np.ceil(x / 10.0)) * 10)

    fig2 = go.Figure()

    fig2.add_trace(go.Indicator(
        mode="number+delta",
        value=ventes_par_mois[12],
        delta={'reference': ventes_par_mois[11]},
        title='December',
    ))

    fig2.update_layout(
        margin=dict(l=0, t=0, r=0, b=0),
        height=100, 
        width=150,
    )

    return fig2



#app.callback figure 3
@app.callback(
    Output('fig-3', 'figure'),
    [Input('location-id', 'value')]
)
def update_frequence_ventes_best(locations):
    data_tmp = data[data['Location'].isin(locations)] if locations else data
    
    sales_by_category_gender = data_tmp.groupby(['Product_Category', 'Gender'])['Frequence'].mean().reset_index()

    sales_by_category_gender_sorted = sales_by_category_gender.groupby(['Product_Category', 'Gender']).mean().reset_index()
    sales_by_category_gender_sorted = sales_by_category_gender_sorted.sort_values(by=['Gender', 'Frequence'], ascending=[True, False])

    top_10_categories_male = sales_by_category_gender_sorted[sales_by_category_gender_sorted['Gender'] == 'M'].head(10)
    top_10_categories_female = sales_by_category_gender_sorted[sales_by_category_gender_sorted['Gender'] == 'F'].head(10)
    
    fig3 = go.Figure()

    fig3.add_trace(go.Bar(
        y=top_10_categories_female['Product_Category'][::-1],
        x=top_10_categories_female['Frequence'][::-1],
        orientation='h',
        name='F',
        marker=dict(color='blue')
    ))
    fig3.add_trace(go.Bar(
        y=top_10_categories_male['Product_Category'][::-1],  
        x=top_10_categories_male['Frequence'][::-1],  
        orientation='h',  
        name='M',
        marker=dict(color='red')
    ))
    fig3.update_layout(
        title='Fréquence des 10 meilleures ventes',
        xaxis_title='Total vente',
        yaxis_title='Catégorie de produit',
        legend_title="Sexe",
        height=650, 
        width=600
    )
    return fig3



#app.callback figure 4 
@app.callback(
    Output('fig-4', 'figure'),
    [Input('location-id', 'value')]
)
def update_evolution_chiffre_affaire(locations):
    data_tmp = data[data['Location'].isin(locations)] if locations else data
    return evolution_chiffre_affaire(data_tmp)

def evolution_chiffre_affaire(df):
    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(x=df.resample('W-Mon', on='Transaction_Date').sum().index,
                              y=df.resample('W-Mon', on='Transaction_Date')['Total_Amount'].sum(),
                              mode="lines"))

    fig4.update_layout(title="Évolution du chiffre d'affaires par semaine",
                       xaxis_title="Semaine",
                       yaxis_title="Chiffre d'affaires",
                       height=400,
                       width=650)
    return fig4



#app.callback tableau
@app.callback(
    Output('fig-5', 'data'),
    [Input('location-id', 'value')]
)
def update_table_data(locations):
    data_tmp = data[data['Location'].isin(locations)] if locations else data
    df_last_100_sales = data_tmp.sort_values(by='Transaction_Date', ascending=False).head(100)
    columns_to_display = ['Date', 'Gender', 'Location', 'Product_Category', 'Quantity', 'Avg_Price', 'Discount_pct']
    return df_last_100_sales[columns_to_display].to_dict('records')


# Exécution de l'application
if __name__ == "__main__":
    app.run(debug=False)