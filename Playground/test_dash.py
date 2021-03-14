import pandas as pd
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go

import dash  # (version 1.12.0) pip install dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

app = dash.Dash(__name__)

# ---------- Import and clean data (importing csv into pandas)
# df = pd.read_csv("intro_bees.csv")
df = pd.read_csv("https://raw.githubusercontent.com/Coding-with-Adam/Dash-by-Plotly/master/Other/Dash_Introduction/intro_bees.csv")

df = df.groupby(['State', 'ANSI', 'Affected by', 'Year', 'state_code'])[['Pct of Colonies Impacted']].mean()
df.reset_index(inplace=True)
print(df[:10])

# ------------------------------------------------------------------------------
# App layout
app.layout = html.Div([

    html.H1("Web Application Dashboards with Dash", style={'text-align': 'left'}),
    html.Div([
        html.Div(
            dcc.Dropdown(id="slct_year",
                 options=[
                     {"label": "2015", "value": 2015},
                     {"label": "2016", "value": 2016},
                     {"label": "2017", "value": 2017},
                     {"label": "2018", "value": 2018}],
                 multi=False,
                 value=2015
                 ), style={'width': "10%",'display': 'inline-block'}),
        html.Div(
            dcc.Dropdown(id="slct_disease",
                 options=[
                     {"label": "Disease", "value": "Disease"},
                     {"label": "Pesticides", "value": "Pesticides"},
                     {"label": "Pests exclude Varroa", "value": "Pests_exl_Varroa"},
                     {"label": "Varroa", "value": "Varroa_mites"},
                     {"label": "Other", "value": "Other"},
                     {"label": "Unknown", "value": "Unknown"}],
                 multi=False,
                 value="Unknown"
                 ), style={'width': "10%",'display': 'inline-block'}),
            ]),
        
    html.Div(id='output_container', children=[], className = "Title"),
    html.Div(id='output_container2', children=[], className = "Title"),
    html.Br(),

    dcc.Graph(id='my_bee_map', figure={}),
    html.Br(),
    dcc.Graph(id='bee_barplot', figure={}),
        
])


# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components


@app.callback(
    Output(component_id='output_container', component_property='children'),
    Output(component_id='output_container2', component_property='children'),
    Output(component_id='my_bee_map', component_property='figure'),
    Output(component_id='bee_barplot', component_property='figure'),
    Input(component_id='slct_year', component_property='value'),
    Input(component_id='slct_disease', component_property='value'),
)

def update_graph(option_slctd, disease_slctd):
    print(option_slctd)
    print(type(option_slctd))

    container = "The year chosen by user was: {}".format(option_slctd)
    container2 = "The disease chosen by user was: {}".format(disease_slctd)

    dff = df.copy()
    dff = dff[dff["Year"] == option_slctd]
    dff = dff[dff["Affected by"] == disease_slctd]

    # Plotly Express
    fig = px.choropleth(
        data_frame=dff,
        locationmode='USA-states',
        locations='state_code',
        scope="usa",
        color='Pct of Colonies Impacted',
        hover_data=['State', 'Pct of Colonies Impacted'],
        color_continuous_scale=px.colors.sequential.YlOrRd,
        labels={'Pct of Colonies Impacted': '% of Bee Colonies'},
        template='plotly_dark'
    )

    dff.sort_values(by="Pct of Colonies Impacted", inplace =True, ascending = False)
    fig2 = px.bar(
        data_frame=dff,
        x = "State",
        y = "Pct of Colonies Impacted",
        color_continuous_scale=px.colors.sequential.YlOrRd,
        labels={'Pct of Colonies Impacted': '% of Bee Colonies'},
        template='plotly_dark'
    )

    # Plotly Graph Objects (GO)
    # fig = go.Figure(
    #     data=[go.Choropleth(
    #         locationmode='USA-states',
    #         locations=dff['state_code'],
    #         z=dff["Pct of Colonies Impacted"].astype(float),
    #         colorscale='Reds',
    #     )]
    # )
    #
    # fig.update_layout(
    #     title_text="Bees Affected by Mites in the USA",
    #     title_xanchor="center",
    #     title_font=dict(size=24),
    #     title_x=0.5,
    #     geo=dict(scope='usa'),
    # )

    return container, container2, fig, fig2


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)