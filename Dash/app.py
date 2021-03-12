import os
import pandas as pd
from time import mktime as mktime
import time
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_table
import dash_bootstrap_components as dbc

from summa import keywords
# from pytopicrank import TopicRank

# Dash core components https://dash.plotly.com/dash-core-components
# Bootstrap components https://dash-bootstrap-components.opensource.faculty.ai/docs/components
# Bootstrap themes https://www.bootstrapcdn.com/bootswatch
BS = "https://stackpath.bootstrapcdn.com/bootswatch/4.5.2/lux/bootstrap.min.css"
app = dash.Dash(external_stylesheets=[BS])

def calculate_timestamps(transcript):
    timestamps = []
    initial_timestamp = datetime.strptime(transcript.minute[0], "%M:%S").replace(year=2000)
    for time in transcript.minute:
        if len(time) == 5:
            timestamp = datetime.strptime(time, "%M:%S").replace(year=2000)
            timestamps.append(mktime(timestamp.timetuple())-mktime(initial_timestamp.timetuple()))
        elif len(time) == 8 and time[5:] == ":00":
            timestamp = datetime.strptime(time[:5], "%M:%S").replace(year=2000)
            timestamps.append(mktime(timestamp.timetuple())-mktime(initial_timestamp.timetuple()))
        elif len(time) == 8:
            timestamp = datetime.strptime(time, "%H:%M:%S").replace(year=2000)
            timestamps.append(mktime(timestamp.timetuple())-mktime(initial_timestamp.timetuple()))
    transcript["timestamp"] = timestamps

transcripts = os.listdir("./transcripts")
initial_transcript_index = 0
initial_transcript = pd.read_csv("./transcripts/" + transcripts[initial_transcript_index])
calculate_timestamps(initial_transcript)
initial_timeline_min = initial_transcript.timestamp[0]
initial_timeline_max = initial_transcript.timestamp[initial_transcript.index[-1]]

#print(initial_timeline_max)
#print(time.gmtime(initial_timeline_max / 1000.0))
#print(time.strftime("%H:%M", time.gmtime(initial_timeline_max)))

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
                        html.Br(),
                        dbc.Button("Apply", id="keyword_extraction_apply_button", color="primary"),
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
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    html.Br(),
                                                    html.H5("Select speaker:"),
                                                    dbc.Checklist(
                                                        id="speaker_selector",
                                                        options=[{"label": i, "value": i}
                                                                for i in sorted(initial_transcript.speaker.unique(),
                                                                                key=str.lower)],
                                                        value=initial_transcript.speaker.unique(),
                                                    ),
                                                ],
                                                width=2,
                                            ),
                                            dbc.Col(
                                                [
                                                    html.Br(),
                                                    html.H5("Select time:"),
                                                    dbc.Row(
                                                        [
                                                            dbc.Col(
                                                                [
                                                                    dbc.Input(
                                                                        id="starttime",
                                                                        type="time",
                                                                        value="00:00",
                                                                    ),
                                                                ],
                                                                width="100px",
                                                            ),
                                                            dbc.Col(
                                                                [
                                                                    dcc.RangeSlider(
                                                                        id="timeline_slider",
                                                                        min=initial_timeline_min,
                                                                        max=initial_timeline_max,
                                                                        value=[initial_timeline_min, initial_timeline_max],
                                                                    ),
                                                                ],
                                                            ),
                                                            dbc.Col(
                                                                [
                                                                    dbc.Input(
                                                                        id="endtime",
                                                                        type="time",
                                                                        value=time.strftime("%H:%M", time.gmtime(initial_timeline_max)),
                                                                    ),
                                                                ],
                                                                width="100px",
                                                            ),
                                                        ],
                                                    ),  
                                                ],
                                                width=6,
                                            ),
                                        ],
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
    Output(component_id="timeline_slider", component_property="min"),
    Output(component_id="timeline_slider", component_property="max"),
    Output(component_id="timeline_slider", component_property="value"),
    Input(component_id="transcript_selector", component_property="value"),
    Input(component_id="speaker_selector", component_property="value"),
)
def update_transcript_table_and_filters(selected_transcript, selected_speakers):
    transcript = pd.read_csv("./transcripts/" + selected_transcript)
    calculate_timestamps(transcript)

    if dash.callback_context.triggered[0]["prop_id"] == "transcript_selector.value":
        speakers = transcript.speaker.unique()
        transcript_table = dbc.Table.from_dataframe(transcript, bordered=True, hover=True)
        timeline_min, timeline_max = transcript.timestamp[0], transcript.timestamp[transcript.index[-1]]

        return (transcript_table, [{"label": i, "value": i} for i in sorted(speakers, key=str.lower)], speakers,
                timeline_min, timeline_max, [timeline_min, timeline_max])

    if dash.callback_context.triggered[0]["prop_id"] == "speaker_selector.value":
        transcript = transcript[transcript.speaker.isin(selected_speakers)]
        transcript_table = dbc.Table.from_dataframe(transcript, bordered=True, hover=True)
        return transcript_table, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

@app.callback(
    Output(component_id="keyword_table", component_property="children"),
    Input(component_id="transcript_selector", component_property="value"),
    Input(component_id="keyword_extraction_apply_button", component_property="n_clicks"),
    State(component_id="keyword_extraction_method_selector", component_property="value"),
)
def extract_keywords(selected_transcript, n_clicks, selected_methods):
    transcript = pd.read_csv("./transcripts/" + selected_transcript)

    if dash.callback_context.triggered[0]["prop_id"] == "keyword_extraction_apply_button.n_clicks":

        if "textrank" in selected_methods:
            textrank_keywords = [None] * len(transcript)
            for i in range(len(transcript)):
                try:
                    textrank_keywords[i] = keywords.keywords(transcript.text[i], words=3).replace("\n", ", ")
                except:
                    textrank_keywords[i] = ""
            transcript["textrank"] = textrank_keywords

        # if "topicrank" in selected_methods:
        #     topicrank_keywords = [None] * len(transcript)
        #     for i in range(len(transcript)):
        #         try:
        #             topicrank_keywords[i] = ", ".join(TopicRank(transcript.text[i]).get_top_n(3))
        #         except:
        #             topicrank_keywords[i] = ""
        #     transcript["topicrank"] = topicrank_keywords

    transcript.drop(columns=["text"], inplace=True)
    return dbc.Table.from_dataframe(transcript, bordered=True, hover=True)

# @app.callback(
#     Output(component_id="speakers_ratio", component_property="figure"),
#     Input(component_id="transcript_selector", component_property="value"),
# )
# def plot_speakers_ratio(selected_transcript):

#     transcript = pd.read_csv("./transcripts/" + selected_transcript)

#     transcript["word_count"] = 0
#     for i in range(len(transcript)):
#         transcript["word_count"][i] = len(transcript["text"][i].split())

#     words_spoken = transcript.groupby(["speaker"]).sum()
#     words_spoken.reset_index(inplace=True)

#     fig = px.bar(words_spoken, x = "speaker", y = "word_count", title="Speaker ratio")
    
#     return fig

if __name__ == "__main__":
    app.run_server(debug=True)
