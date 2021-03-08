import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_table
import dash_bootstrap_components as dbc

from summa import keywords
from pytopicrank import TopicRank

# Themes can be found at https://www.bootstrapcdn.com/bootswatch/
BS = "https://stackpath.bootstrapcdn.com/bootswatch/4.5.2/litera/bootstrap.min.css"
app = dash.Dash(external_stylesheets=[BS])

transcripts = os.listdir("./transcripts")
initial_transcript_index = 2
initial_transcript = pd.read_csv("./transcripts/" + transcripts[initial_transcript_index])

app.layout = dbc.Container(
    [
        html.Br(),
        html.H1("Dialog Summarization", style={"text-align": "center"}),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Select(
                            id="transcript_selector",
                            options=[{"label": i, "value": i} for i in transcripts],
                            value=transcripts[initial_transcript_index],
                        ),
                    ],
                    width=3,
                ),
                dbc.Col(
                    [
                        dbc.Checklist(
                            id="keyword_extraction_method_selector",
                            options=[
                                {"label": "Word frequency", "value": "word_frequency"},
                                {"label": "TF-IDF", "value": "tf_idf"},
                                {"label": "TextRank", "value": "textrank"},
                                {"label": "TopicRank", "value": "topicrank"},
                                {"label": "YAKE!", "value": "yake"},
                                {"label": "BERT", "value": "bert"},
                            ],
                            value=[],
                            switch=True,
                        ),
                        dbc.Button("Apply", id="keyword_extraction_apply_button"),
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
                                dbc.Tab(label="Transcript", children=[
                                    html.Div(
                                        [
                                            html.Br(),
                                            html.H5("Select speaker:"),
                                            dbc.Checklist(
                                                id="speaker_selector",
                                                options=[{"label": i, "value": i}
                                                         for i in initial_transcript.speaker.unique()],
                                                value=initial_transcript.speaker.unique(),
                                            ),
                                        ],
                                        style={
                                            "width": "300px"
                                        },
                                    ),
                                    html.Br(),
                                    html.Div(id="transcript_table", children=[
                                        dbc.Table.from_dataframe(initial_transcript, bordered=True, hover=True)
                                    ],
                                    ),
                                ],
                                ),
                                dbc.Tab(label="Keywords", children=[
                                    html.Br(),
                                    html.Div(id="keyword_table", children=[
                                        dbc.Table.from_dataframe(initial_transcript, bordered=True, hover=True)
                                    ],
                                    ),
                                ],
                                ),
                                dbc.Tab(label="Plots", children=[
                                    dcc.Graph(id="speakers_ratio", figure={}),
                                ],
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ],
    fluid=True,
)

@app.callback(
    Output(component_id="transcript_table", component_property="children"),
    Output(component_id="speaker_selector", component_property="options"),
    Output(component_id="speaker_selector", component_property="value"),
    Input(component_id="transcript_selector", component_property="value"),
    Input(component_id="speaker_selector", component_property="value"),
)
def update_transcript_table_and_filters(selected_transcript, selected_speakers):
    transcript = pd.read_csv("./transcripts/" + selected_transcript)
    
    if dash.callback_context.triggered[0]["prop_id"] == "transcript_selector.value":
        speakers = transcript.speaker.unique()
        table = dbc.Table.from_dataframe(transcript, bordered=True, hover=True)
        return table, [{"label": i, "value": i} for i in speakers], speakers
    
    if dash.callback_context.triggered[0]["prop_id"] == "speaker_selector.value":
        transcript = transcript[transcript.speaker.isin(selected_speakers)]
        table = dbc.Table.from_dataframe(transcript, bordered=True, hover=True)
        return table, dash.no_update, dash.no_update

    return dash.no_update, dash.no_update, dash.no_update

@app.callback(
    Output(component_id="keyword_table", component_property="children"),
    Input(component_id="transcript_selector", component_property="value"),
    Input(component_id="keyword_extraction_apply_button", component_property="n_clicks"),
    State(component_id="keyword_extraction_method_selector", component_property="value"),
)
def extract_keywords(selected_transcript, n_clicks, selected_methods):
    transcript = pd.read_csv("./transcripts/" + selected_transcript)

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
    table = dbc.Table.from_dataframe(transcript, bordered=True, hover=True)
    return table

@app.callback(
    Output(component_id="speakers_ratio", component_property="figure"),
    Input(component_id="transcript_selector", component_property="value"),
)
def plot_speakers_ratio(selected_transcript):

    transcript = pd.read_csv("./transcripts/" + selected_transcript)

    transcript["word_count"] = 0
    for i in range(len(transcript)):
        transcript["word_count"][i] = len(transcript["text"][i].split())

    words_spoken = transcript.groupby(["speaker"]).sum()
    words_spoken.reset_index(inplace=True)

    fig = px.bar(words_spoken, x = "speaker", y = "word_count", title="Speaker ratio")
    
    return fig

if __name__ == "__main__":
    app.run_server(debug=True)
