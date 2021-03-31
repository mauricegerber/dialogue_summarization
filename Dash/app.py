import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
import time
import base64
import io
import re
import math

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import dash_table

import plotly.express as px
import plotly.graph_objects as go

from nltk.corpus import stopwords

sys.path.insert(0, "./lib")
import texttiling

# https://bootswatch.com/lux/
BS = "https://stackpath.bootstrapcdn.com/bootswatch/4.5.2/lux/bootstrap.min.css"
app = dash.Dash(external_stylesheets=[BS])

def calculate_timestamps(transcript):
    first_timestamp = datetime.strptime("0:00", "%M:%S")
    timestamps = []
    for t in transcript["Time"]:
        if len(t) <= 5:
            current_timestamp = datetime.strptime(t, "%M:%S")
            timestamps.append(int((current_timestamp - first_timestamp).total_seconds()))
        else:
            current_timestamp = datetime.strptime(t, "%H:%M:%S")
            timestamps.append(int((current_timestamp - first_timestamp).total_seconds()))
    transcript["Timestamp"] = timestamps

transcripts_dir = "./transcripts/"
transcript_files = os.listdir(transcripts_dir)
initial_transcript_index = 1

transcripts = []
for file in transcript_files:
    transcript = pd.read_csv(
        filepath_or_buffer=transcripts_dir + file,
        header=0,
        names=["Speaker", "Time", "End time", "Duration", "Utterance"],
        usecols=["Speaker", "Time", "Utterance"]
    )
    transcript["Time"] = transcript["Time"].str.replace("60", "59")
    calculate_timestamps(transcript)
    transcripts.append(transcript)

initial_transcript = transcripts[initial_transcript_index]
initial_timeline_min = initial_transcript["Timestamp"][0]
initial_timeline_max = initial_transcript["Timestamp"][len(initial_transcript)-1]

vertical_space = "15px"

app.layout = dbc.Container(
    [
        html.H1("Dialog analyzer"),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Select(
                            id="transcript_selector",
                            options=[{"label": transcript_files[i], "value": i} for i in range(len(transcript_files))],
                            value=initial_transcript_index,
                        ),
                    ],
                    width=3,
                ),
                dbc.Col(
                    [
                        dcc.Upload(
                            id="transcript_upload_button",
                            children=[
                                dbc.Button(
                                    "Upload",
                                    className="btn-outline-primary",
                                    style={"width": "100%"},
                                ),
                            ],
                        ),
                        dbc.Modal(
                            id="modal_upload",
                            children=[
                                dbc.ModalHeader("Upload successful"),
                                dbc.ModalBody(
                                    html.Div(id="output_file")
                                ),
                                dbc.ModalFooter(
                                    dbc.Button("Close", id="close", className="ml-auto")
                                ),
                            ],
                        ),
                    ],
                    width=1,
                ),
                dbc.Col(
                    [
                        dbc.Button(
                            "Delete",
                            id="transcript_delete_button",
                            className="btn-outline-primary",
                            style={"width": "100%"},
                        ),
                    ],
                    width=1,
                ),
            ],
            align="center",
        ),
        html.Div(style={"height": vertical_space}),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Tabs(
                            [
                                dbc.Tab(label="Transcript", children=[
                                    html.Div(style={"height": vertical_space}),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    html.H5("Select speaker"),
                                                    dbc.Checklist(
                                                        id="speaker_selector",
                                                        options=[{"label": i, "value": i}
                                                                 for i in sorted(initial_transcript["Speaker"].unique(),
                                                                 key=str.lower)],
                                                        value=initial_transcript["Speaker"].unique(),
                                                    ),
                                                ],
                                                width="auto",
                                            ),
                                            dbc.Col(
                                                [
                                                    html.H5("Select time"),
                                                    dbc.Row(
                                                        [
                                                            dbc.Col(
                                                                [
                                                                    dbc.Input(
                                                                        id="start_time_input",
                                                                        type="time",
                                                                        value="00:00",
                                                                    ),
                                                                ],
                                                                width="auto",
                                                            ),
                                                            dbc.Col(
                                                                [
                                                                    dcc.RangeSlider(
                                                                        id="timeline_slider",
                                                                        min=initial_timeline_min,
                                                                        max=initial_timeline_max,
                                                                        value=[initial_timeline_min, initial_timeline_max],
                                                                        marks={},
                                                                    ),
                                                                ],
                                                            ),
                                                            dbc.Col(
                                                                [
                                                                    dbc.Input(
                                                                        id="end_time_input",
                                                                        type="time",
                                                                        value=time.strftime("%H:%M", time.gmtime(initial_timeline_max)),
                                                                    ),
                                                                ],
                                                                width="auto",
                                                            ),
                                                        ],
                                                    ),  
                                                ],
                                                style={"margin": "0px 100px 0px"},
                                            ),
                                            dbc.Col(
                                                [
                                                    html.H5("Search"),
                                                    dbc.Input(
                                                        id="search_input",
                                                        type="text",
                                                        placeholder="Enter search term here",
                                                    ),
                                                ],
                                                width="auto",
                                            ),
                                        ],
                                    ),
                                    html.Div(style={"height": vertical_space}),
                                    dash_table.DataTable(
                                        id="transcript_table",
                                        columns=[
                                            {"name": "Speaker", "id": "Speaker", "presentation": "markdown"},
                                            {"name": "Time", "id": "Time", "presentation": "markdown"},
                                            {"name": "Utterance", "id": "Utterance", "presentation": "markdown"}
                                        ],
                                        data=initial_transcript[["Speaker", "Time", "Utterance"]].to_dict("records"),
                                        style_data_conditional=[
                                            {"if": {"state": "selected"},
                                             "background-color": "white",
                                             "border": "1px solid rgba(0,0,0,0.05)"},
                                        ],
                                        style_header={
                                            "font-size": "0.9rem",
                                            "background-color": "#f7f7f9",
                                            "border": "1px solid rgba(0,0,0,0.05)",
                                        },
                                        style_cell_conditional=[
                                            {"if": {"column_id": "Speaker"},
                                             "width": "150px"},
                                            {"if": {"column_id": "Time"},
                                             "width": "100px"},
                                            {"if": {"column_id": "Utterance"},
                                             "width": "1450px"},
                                        ],
                                        style_cell={
                                            "white-space": "normal",
                                            "padding": "1.5rem",
                                            "border": "1px solid rgba(0,0,0,0.05)",   
                                        },
                                        fixed_rows={"headers": True},
                                        page_action="none",
                                    ),
                                ],
                                ),
                                dbc.Tab(label="Keywords", children=[
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    html.Br(),
                                                    dbc.Button("Apply", id="apply_texttiling_settings"),
                                                ],
                                                width=1,
                                            ),
                                            dbc.Col(
                                                [
                                                    html.Br(),
                                                    html.H5("Additional stopwords"),
                                                    dbc.Input(
                                                        id="stopwords_input",
                                                        type="text",
                                                        placeholder="Enter additional stopwords here (comma-separated)",
                                                    ),
                                                ],
                                                width=4,
                                            ),
                                            dbc.Col(
                                                [
                                                    html.Br(),
                                                    html.H5("Change parameters"),
                                                    dbc.Row(
                                                        [
                                                            dbc.Col(
                                                                [
                                                                    html.P("Pseudosentence length (10-30)"),
                                                                ],
                                                                #width=8,
                                                            ),
                                                            dbc.Col(
                                                                [
                                                                    dbc.Input(
                                                                        id="window_size_input",
                                                                        type="number",
                                                                        min=5,
                                                                        max=20,
                                                                        step=1,
                                                                        value=10,
                                                                    ),
                                                                ],
                                                                #width=4,
                                                            ),                       
                                                        ],
                                                    ),
                                                    dbc.Row(
                                                        [
                                                            dbc.Col(
                                                                [
                                                                    html.P("Window size (10-30)"),
                                                                ],
                                                                #width=8,
                                                            ),
                                                            dbc.Col(
                                                                [
                                                                    dbc.Input(
                                                                        id="window_size_input2",
                                                                        type="number",
                                                                        min=5,
                                                                        max=20,
                                                                        step=1,
                                                                        value=10,
                                                                    ),
                                                                ],
                                                                #width=4,
                                                            ),                       
                                                        ],
                                                    ),
                                                    html.Br(),
                                                ],
                                                width=2,
                                            ),
                                        ],
                                    ),  
                                    dcc.Graph(id="keywords_plot", figure={}, config={"displayModeBar": False}),      
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
    Output(component_id="transcript_table", component_property="data"),
    Output(component_id="speaker_selector", component_property="options"),
    Output(component_id="speaker_selector", component_property="value"),
    Output(component_id="start_time_input", component_property="value"),
    Output(component_id="end_time_input", component_property="value"),
    Output(component_id="timeline_slider", component_property="min"),
    Output(component_id="timeline_slider", component_property="max"),
    Output(component_id="timeline_slider", component_property="value"),
    Output(component_id="timeline_slider", component_property="marks"),
    Output(component_id="search_input", component_property="value"),
    Input(component_id="transcript_selector", component_property="value"),
    Input(component_id="speaker_selector", component_property="value"),
    Input(component_id="start_time_input", component_property="value"),
    Input(component_id="end_time_input", component_property="value"),
    Input(component_id="timeline_slider", component_property="value"),
    Input(component_id="search_input", component_property="value"),
)
def update_transcript_table_and_filters(selected_transcript, selected_speaker, selected_start_time,
                                        selected_end_time, selected_timeline, search_term):
    transcript = transcripts[int(selected_transcript)] # selected_transcript is str, must be int

    timeline_min = transcript["Timestamp"][0]
    timeline_max = transcript["Timestamp"][len(transcript)-1]
    # difference between timeline_max and start of last minute, e.g. 44:21 - 44:00 = 00:21
    timeline_deviation = timeline_max - math.floor(timeline_max/60)*60
    marks = dict()

    trigger = dash.callback_context.triggered[0]["prop_id"]

    if trigger == "transcript_selector.value":
        speakers = transcript["Speaker"].unique()
        transcript_table = transcript[["Speaker", "Time", "Utterance"]].to_dict("records")
        
        return (transcript_table, [{"label": i, "value": i} for i in sorted(speakers, key=str.lower)], speakers,
                "00:00", time.strftime("%H:%M", time.gmtime(timeline_max)),
                timeline_min, timeline_max, [timeline_min, timeline_max], marks, None)
    
    if trigger != "." and trigger != "transcript_selector.value":
        transcript = transcript[transcript["Speaker"].isin(selected_speaker)]
        
        # if double letter occurs, word highlighting does not work properly due to markdown syntax
        # therefore, search is only enabled for search terms longer than 1 character
        if search_term != None and len(search_term) > 1:
            transcript = transcript[transcript["Utterance"].str.contains(search_term, case=False, regex=False)]
            # if last character in search_term is a space, word highlighting does not work properly due to markdown syntax
            # therefore, it is stripped while highlighting (but not in the search field)
            if search_term[-1] == " ":
                transcript["Utterance"] = transcript["Utterance"].str.replace(search_term[:-1], "**" + search_term[:-1] + "**", case=False)
            else:
                transcript["Utterance"] = transcript["Utterance"].str.replace(search_term, "**" + search_term + "**", case=False)
            marks = dict(zip(transcript["Timestamp"], ["|"] * len(transcript)))
            
        if trigger == "start_time_input.value" or trigger == "end_time_input.value":
            # in Firefox the input field can be cleared by clicking the encircled X (which cannot be hidden)
            # this causes an error with the datetime conversion and is therefore handled as exception
            try:
                first_timestamp = datetime.strptime("0:00", "%M:%S")
                current_start_time = datetime.strptime(selected_start_time, "%H:%M")
                current_end_time = datetime.strptime(selected_end_time, "%H:%M")
                # timeline_deviation is added to prevent last utterances from being filtered out
                # e.g. if 00:44 is entered, utterances from 00:44:01 to 00:44:21 would be filtered out if timeline_deviation was not added
                timeline_slider_values = [(current_start_time - first_timestamp).total_seconds(),
                                          (current_end_time - first_timestamp).total_seconds() + timeline_deviation]
                transcript = transcript[transcript["Timestamp"] >= timeline_slider_values[0]]
                transcript = transcript[transcript["Timestamp"] <= timeline_slider_values[1]]
                transcript_table = transcript[["Speaker", "Time", "Utterance"]].to_dict("records")

                return (transcript_table, dash.no_update, dash.no_update, dash.no_update, dash.no_update,
                        dash.no_update, dash.no_update, timeline_slider_values, dash.no_update, dash.no_update)
            except:
                pass

        transcript = transcript[transcript["Timestamp"] >= selected_timeline[0]]
        transcript = transcript[transcript["Timestamp"] <= selected_timeline[1]]
        transcript_table = transcript[["Speaker", "Time", "Utterance"]].to_dict("records")

        return (transcript_table, dash.no_update, dash.no_update,
                time.strftime("%H:%M", time.gmtime(selected_timeline[0])),
                time.strftime("%H:%M", time.gmtime(selected_timeline[1])),
                dash.no_update, dash.no_update, dash.no_update, marks, dash.no_update)

    return (dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update,
            dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update)

@app.callback(
    Output(component_id="keywords_plot", component_property="figure"),
    Input(component_id="apply_texttiling_settings", component_property="n_clicks"),
    State(component_id="transcript_selector", component_property="value"),
    State(component_id="stopwords_input", component_property="value"),
)
def create_keywords_plot(n_clicks, selected_transcript, additional_stopwords):
    transcript = transcripts[int(selected_transcript)]
    
    additional_stopwords_list = []
    if additional_stopwords != None:
        additional_stopwords_list = additional_stopwords.split(",")
    sw = set(stopwords.words("english") + additional_stopwords_list)

    boundaries, depth_scores = texttiling.texttiling(transcript, sw)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=list(range(len(depth_scores))),
        y=depth_scores,
        mode="lines"
    ))

    return fig

def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
 
    try:
        df = pd.read_csv(
            filepath_or_buffer=io.StringIO(decoded.decode('utf-8')),
            header=0,
            names=["Speaker", "Time", "End time", "Duration", "Utterance"],
            usecols=["Speaker", "Time", "Utterance"]
        )
        
    except Exception as e:
        return html.Div(['There was an error processing this file.'])
        
    return df

@app.callback(
    Output(component_id="transcript_selector", component_property="options"),
    Output(component_id="modal_upload", component_property="is_open"),
    Output(component_id="output_file", component_property="children"),
    Input(component_id="transcript_upload_button", component_property="contents"),
    Input(component_id="close", component_property="n_clicks"),
    State(component_id="transcript_upload_button", component_property="filename"),
    State(component_id="transcript_upload_button", component_property="last_modified"),
    State(component_id="modal_upload", component_property="is_open"))
def update_transcripts(list_of_contents, modal_upload_input, list_of_names, list_of_dates, is_open):
    if is_open == True:
        return dash.no_update, False, ""

    if list_of_contents is not None:
        transcript = parse_contents(list_of_contents, list_of_names, list_of_dates)
        
        transcript["Time"] = transcript["Time"].str.replace("60", "59")
        calculate_timestamps(transcript)
        
        transcripts.append(transcript)
        transcript_files.append(list_of_names)

        index = len(list_of_names) - list_of_names.find(".",(len(list_of_names)-5))
        output_name = list_of_names[:-index] + " is now available in the Dropdown Menue"
        return [{"label": transcript_files[i], "value": i} for i in range(len(transcript_files))], True, output_name

    return [{"label": transcript_files[i], "value": i} for i in range(len(transcript_files))], False, ""






# @app.callback(
#     Output(component_id="keyword_table", component_property="children"),
#     Input(component_id="transcript_selector", component_property="value"),
#     Input(component_id="keyword_extraction_apply_button", component_property="n_clicks"),
#     State(component_id="keyword_extraction_method_selector", component_property="value"),
# )
# def extract_keywords(selected_transcript, n_clicks, selected_methods):
#     transcript = pd.read_csv("./transcripts/" + selected_transcript)

#     if dash.callback_context.triggered[0]["prop_id"] == "keyword_extraction_apply_button.n_clicks":

#         if "textrank" in selected_methods:
#             textrank_keywords = [None] * len(transcript)
#             for i in range(len(transcript)):
#                 try:
#                     textrank_keywords[i] = keywords.keywords(transcript.text[i], words=3).replace("\n", ", ")
#                 except:
#                     textrank_keywords[i] = ""
#             transcript["textrank"] = textrank_keywords

#         # if "topicrank" in selected_methods:
#         #     topicrank_keywords = [None] * len(transcript)
#         #     for i in range(len(transcript)):
#         #         try:
#         #             topicrank_keywords[i] = ", ".join(TopicRank(transcript.text[i]).get_top_n(3))
#         #         except:
#         #             topicrank_keywords[i] = ""
#         #     transcript["topicrank"] = topicrank_keywords

#     transcript.drop(columns=["text"], inplace=True)
#     return dbc.Table.from_dataframe(transcript, bordered=True, hover=True)

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
    # context = ("/etc/letsencrypt/live/projects.pascalaigner.ch/cert.pem", "/etc/letsencrypt/live/projects.pascalaigner.ch/privkey.pem")
    app.run_server(
        # host="projects.pascalaigner.ch",
        # port=443,
        # ssl_context=context,
        debug=True)
