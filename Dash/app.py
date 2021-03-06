import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import dash_table
import os

from summa import keywords
from pytopicrank import TopicRank

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

transcripts = os.listdir("./transcripts")
initial_transcript_index = 4
initial_transcript = pd.read_csv("./transcripts/" + transcripts[initial_transcript_index])

app.layout = dbc.Container(
    [
        html.H1("Web Application Dashboards with Dash", style={'text-align': 'center'}),
        
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Dropdown(
                            id="transcript_selector",
                            options=[{"label": i, "value": i} for i in transcripts],
                            value=transcripts[initial_transcript_index],
                        ),
                    ],
                    width=3,
                ),
                dbc.Col(
                    [
                        dcc.Checklist(
                            id="keyword_extraction_method_selector",
                            options=[
                                {"label": "Word frequency", "value": "word_frequency"},
                                {"label": "TF-IDF", "value": "tf_idf"},
                                {"label": "TextRank", "value": "textrank"},
                                {"label": "TopicRank", "value": "topicrank"},
                                {"label": "YAKE!", "value": "yake"},
                                {"label": "BERT", "value": "bert"}
                            ],
                            value=[],
                            labelStyle={
                                "display": "block"
                            },
                        ),
                    ],
                    width=3,
                ),
            ],
        ),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Tabs(
                            [
                                dbc.Tab(label="Transcript", tab_id="tab1", children=[
                                    html.Br(),
                                    dash_table.DataTable(
                                        id="transcript_table",
                                        columns=[
                                            {"name": "Speaker", "id": "speaker"},
                                            {"name": "Timestamp", "id": "minute"},
                                            {"name": "Text", "id": "text"}
                                        ],
                                        data=initial_transcript.to_dict("records"),
                                        style_cell={
                                            "font-family": "sans-serif",
                                            "white-space": "normal",
                                            "text-align": "left"
                                        },
                                        editable=False,
                                    ),
                                ],
                                ),
                                dbc.Tab(label="Keywords", tab_id="tab2", children=[
                                    dash_table.DataTable(
                                        id="keywords_table",
                                        style_cell={
                                            "font-family": "sans-serif",
                                            "white-space": "normal",
                                            "text-align": "left"
                                        },
                                        editable=False,
                                    ),
                                    html.Div(id='output_container', children=[]),
                                ],
                                ),
                                dbc.Tab(label="Plots", tab_id="tab3", children=[
                                    dcc.Graph(id="speakers_ratio", figure={}),
                                ],
                                ),
                            ],
                            id="tabs"
                        ),
                    ],
                ),
            ],
        ),
    ],
    fluid=True,
)

@app.callback(
    Output(component_id="transcript_table", component_property="data"),
    Input(component_id="transcript_selector", component_property="value"),
)
def update_transcript_table(selected_transcript):
    return pd.read_csv("./transcripts/" + selected_transcript).to_dict("records")

@app.callback(
    Output(component_id="keywords_table", component_property="columns"),
    Output(component_id="keywords_table", component_property="data"),
    Input(component_id="keyword_extraction_method_selector", component_property="value"),
    Input(component_id="transcript_table", component_property="data"),
)
def extract_keywords(selected_methods, transcript_table):

    transcript = pd.DataFrame.from_records(transcript_table)
    
    if "textrank" in selected_methods:
        textrank_keywords = [None] * len(transcript)
        for i in range(len(transcript)):
            try:
                textrank_keywords[i] = keywords.keywords(transcript["text"][i], words=3).replace("\n", ", ")
            except:
                textrank_keywords[i] = ""
        transcript["textrank"] = textrank_keywords

    if "topicrank" in selected_methods:
        topicrank_keywords = [None] * len(transcript)
        for i in range(len(transcript)):
            try:
                topicrank_keywords[i] = ", ".join(TopicRank(transcript["text"][i]).get_top_n(3))
            except:
                topicrank_keywords[i] = ""
        transcript["topicrank"] = topicrank_keywords
    
    transcript.drop(columns=["text"], inplace=True)

    return [{"name": i, "id": i} for i in transcript.columns], transcript.to_dict("records")

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

if __name__ == "__main__":
    app.run_server(debug=True)
