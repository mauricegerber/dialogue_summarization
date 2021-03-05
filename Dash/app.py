import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table

import os

app = dash.Dash(__name__)

# ---------- Preprocessing ----------
for root, dirs, files in os.walk("./transcripts"):
    transcripts = files

transcript_init = pd.read_csv("./transcripts/" + files[0])

# ---------- App layout ----------
app.layout = html.Div([

    html.H1("Web Application Dashboards with Dash", style={'text-align': 'center'}),

    dcc.Dropdown(
        id="select_transcript",
        options=[{"label": i, "value": i} for i in transcripts],
        value=transcripts[0]
    ),

    html.Br(),

    dcc.Graph(id='speakers_ratio', figure={}),

    html.Br(),

    dash_table.DataTable(
        id="transcript_table",
        columns=[{'name': 'speaker', 'id': 'speaker'},
                 {'name': 'minute', 'id': 'minute'},
                 {'name': 'text', 'id': 'text'}],
        data=transcript_init.to_dict("records"),
        style_cell={
            "whiteSpace": "normal",
            "height": "auto",
            "textAlign": "left",
            "font-family": "sans-serif",
        },
    )
])

# ---------- Callbacks ----------
@app.callback(
    Output(component_id="transcript_table", component_property="data"),
    Input(component_id="select_transcript", component_property="value")
)
def update_datatable(selected_transcript):
    transcript = pd.read_csv("./transcripts/" + selected_transcript)
    return transcript.to_dict('records')

@app.callback(
    Output(component_id="speakers_ratio", component_property="figure"),
    Input(component_id="transcript_table", component_property="data")
)
def plot_speakers_ratio(selected_transcript):

    transcript = pd.DataFrame.from_records(selected_transcript)

    transcript["word_count"] = 0
    for i in range(len(transcript)):
        transcript["word_count"][i] = len(transcript["text"][i].split())

    words_spoken = transcript.groupby(["speaker"]).sum()
    words_spoken.reset_index(inplace=True)

    fig = px.bar(words_spoken, x = "speaker", y = "word_count", title="Speaker ratio")
    
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
