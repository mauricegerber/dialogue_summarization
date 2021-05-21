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
import random

import flask
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import dash_table

import plotly.express as px
import plotly.graph_objects as go

from nltk.corpus import stopwords
from keybert import KeyBERT
kw_extractor = KeyBERT('distilbert-base-nli-mean-tokens')
from sklearn.preprocessing import MinMaxScaler

from sklearn.feature_extraction.text import TfidfVectorizer

sys.path.insert(0, "./lib")
import texttiling
import create_pdf
import split_dialog
import wordcloud_pl
import tf_idf
import tfidf

# TO DO
# erstellte PDF direkt nach neuem generieren löschen
# Transkribtname in Dateiname

# https://bootswatch.com/lux/
BS = "https://stackpath.bootstrapcdn.com/bootswatch/4.5.2/lux/bootstrap.min.css"
app = dash.Dash(external_stylesheets=[BS])
app.title = "Dialog Analyzer"

def calculate_timestamps(transcript):
    ft = datetime.strptime("00:00:00", "%H:%M:%S")
    timestamps_hms = []
    timestamps_s = []
    # time column has format %M:%S and minutes can exceed 59
    # e.g. time value of 65:46 corresponds to 01:05:46 in %H:%M:%S format
    for t in transcript["Time"]:
        t = t.split(":")
        h = math.floor(int(t[0]) / 60)
        m = int(t[0]) % 60
        s = t[1]
        if s == "60": s = "59" # seconds can have value of 60 which would be non-convertible
        hms = ":".join([str(h), str(m), s])
        ct = datetime.strptime(hms, "%H:%M:%S")
        if ct.hour == 0:
            timestamps_hms.append("{:02d}:{:02d}".format(ct.minute, ct.second))
        else:
            timestamps_hms.append("{:02d}:{:02d}:{:02d}".format(ct.hour, ct.minute, ct.second))
        timestamps_s.append(int((ct - ft).total_seconds()))
    transcript["Time"] = timestamps_hms
    transcript["Timestamp"] = timestamps_s

transcripts_dir = "./transcripts/"
transcript_files = os.listdir(transcripts_dir)
initial_transcript_index = 0

transcripts = []
for f in transcript_files:
    transcript = pd.read_csv(
        filepath_or_buffer=transcripts_dir + f,
        header=0,
        names=["Speaker", "Time", "End time", "Duration", "Utterance"],
        usecols=["Speaker", "Time", "Utterance"]
    )
    calculate_timestamps(transcript)
    transcripts.append(transcript)

initial_transcript = transcripts[initial_transcript_index]
initial_timeline_min = initial_transcript["Timestamp"][0]
initial_timeline_max = initial_transcript["Timestamp"][len(initial_transcript)-1]

vertical_space = "15px"

app.layout = dbc.Container(
    [
        html.H1("Dialog Analyzer"),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Select(
                            id="transcript_selector",
                            options=[{"label": transcript_files[i], "value": str(i)} for i in range(len(transcript_files))],
                            value=str(initial_transcript_index),
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
                                ),
                            ],
                        ),
                        dbc.Modal(
                            id="modal",
                            children=[
                                dbc.ModalHeader(id="modal_header", children=[]),
                                dbc.ModalBody(id="modal_body", children=[]),
                                dbc.ModalFooter(
                                    dbc.Button(
                                        "Close",
                                        id="modal_close_button",
                                        className="btn-outline-primary",
                                    ),
                                ),
                            ],
                        ),
                    ],
                    width="auto",
                ),
                dbc.Col(
                    [
                        dbc.Button(
                            "Delete",
                            id="transcript_delete_button",
                            className="btn-outline-primary",
                        ),
                    ],
                    width="auto",
                ),
                dbc.Col([]),
                dbc.Col(
                    [
                        dbc.Button(
                            "Generate PDF",
                            id="pdf_generate_button",
                            className="btn-outline-danger",
                        ),
                    ],
                    width="auto",
                ),
                dbc.Col(
                    [  
                        html.Div(
                            id="download-area",
                            className="block",
                            children=[
                                dbc.Button(
                                    "Download",
                                    id="pdf_download_button",
                                    className="btn-secondary disabled",
                                    disabled = True
                                ) 
                            ]
                        )
                    ],
                    width="auto",
                ),
            ],
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
                                                    html.H5("Speakers"),
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
                                                    html.H5("Timeline"),
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
                                                style={"margin": "0% 5% 0%"},
                                            ),
                                            dbc.Col(
                                                [
                                                    html.H5("Search"),
                                                    dbc.Input(
                                                        id="search_input",
                                                        type="text",
                                                        placeholder="Enter search term",
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
                                             "border": "1px solid #e9e9e9"},
                                        ],
                                        style_header={
                                            "text-align": "left",
                                            "font-family": "sans-serif",
                                            "font-size": "13px",
                                            "background-color": "#f7f7f9",
                                            "border": "none",
                                        },
                                        style_cell_conditional=[
                                            # real column widths in browser differ from these values
                                            # these values provide good ratio between columns widths
                                            {"if": {"column_id": "Speaker"},
                                             "width": "30px"},
                                            {"if": {"column_id": "Time"},
                                             "width": "30px"},
                                            {"if": {"column_id": "Utterance"},
                                             "width": "800px"},
                                        ],
                                        style_cell={
                                            "white-space": "normal", # required for line breaks in utterance column
                                            "padding": "15px",
                                            "border": "1px solid #e9e9e9",   
                                        },
                                        css=[
                                            # sum of absolute elements 30+38+30+52+15+38+15+72(variable)+15...+15+21+15
                                            {"selector": ".dash-freeze-top",
                                             "rule": "max-height: calc(100vh - 356px)"},
                                            ],
                                        fixed_rows={"headers": True},
                                        page_action="none",
                                    ),
                                ],
                                ),
                                dbc.Tab(label="TextTiling", children=[
                                    html.Div(style={"height": vertical_space}),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    html.H5("Language"),
                                                    dbc.RadioItems(
                                                        id="language_radio_button",
                                                        options=[
                                                            {"label": "English", "value": "english"},
                                                            {"label": "German", "value": "german"},
                                                        ],
                                                        value="english",
                                                    ),
                                                ],
                                                width="auto",
                                            ),
                                            dbc.Col(
                                                [
                                                    html.H5("Additional stopwords"),
                                                    dbc.Input(
                                                        id="stopwords_input",
                                                        type="text",
                                                        placeholder="Enter additional stopwords separated by comma",
                                                    ),
                                                ],
                                                style={"margin": "0% 3% 0%"},
                                            ),
                                            dbc.Col(
                                                [
                                                    html.H5("Parameters"),
                                                    dbc.Row(
                                                        [
                                                            dbc.Col(
                                                                [
                                                                    html.Div("Pseudosentence"),
                                                                    html.Div("length w"),
                                                                ],
                                                                width="auto",
                                                            ),
                                                            dbc.Col(
                                                                [
                                                                    dbc.Input(
                                                                        id="pseudosentence_length_input",
                                                                        type="number",
                                                                        step=1,
                                                                        value=20,
                                                                    ),
                                                                ],
                                                                width="auto",
                                                            ),
                                                            dbc.Col(
                                                                [
                                                                    html.Div("Block size k"),
                                                                ],
                                                                width="auto",
                                                            ),
                                                            dbc.Col(
                                                                [
                                                                    dbc.Input(
                                                                        id="block_size_input",
                                                                        type="number",
                                                                        step=1,
                                                                        value=10,
                                                                    ),
                                                                ],
                                                                width="auto",
                                                            ),
                                                            dbc.Col(
                                                                [
                                                                    html.Div("Number of"),
                                                                    html.Div("subtopics n"),
                                                                ],
                                                                width="auto",
                                                            ),
                                                            dbc.Col(
                                                                [
                                                                    dbc.Input(
                                                                        id="n_topics_input",
                                                                        type="number",
                                                                        step=1,
                                                                        value=3,
                                                                    ),
                                                                ],
                                                                width="auto",
                                                            ),
                                                        ],
                                                    ),
                                                ],
                                                width="auto",
                                                style={"margin": "0% 3% 0% 0%"},
                                            ),
                                            dbc.Col(
                                                [
                                                    html.Div(style={"height": "27px"}),
                                                    dbc.Button(
                                                        "Apply",
                                                        id="apply_texttiling_settings",
                                                        className="btn-outline-primary",
                                                    ),
                                                ],
                                                width="auto",
                                            ),
                                        ],
                                    ),
                                    html.Div(style={"height": vertical_space}),
                                    dcc.Loading(
                                        id="loading1",
                                        color="#1a1a1a",
                                        children=[
                                            dcc.Graph(
                                                id="texttiling_plot",
                                                figure={"layout": go.Layout(margin={"t": 0, "b": 0, "r": 0, "l": 0})},
                                                config={"displayModeBar": False},
                                                style={"height": "250px"},
                                            ),
                                            html.Div(style={"height": vertical_space}),
                                            dash_table.DataTable(
                                                id="texttiling_table",
                                                columns=[
                                                    {"name": "Time", "id": "Start time", "presentation": "markdown"},
                                                    {"name": "Keywords (tf-idf)", "id": "Keywords", "presentation": "markdown"},
                                                ],
                                                style_data_conditional=[
                                                    {"if": {"state": "selected"},
                                                     "background-color": "white",
                                                     "border": "1px solid #e9e9e9"},
                                                ],
                                                style_header={
                                                    "text-align": "left",
                                                    "font-family": "sans-serif",
                                                    "font-size": "13px",
                                                    "background-color": "#f7f7f9",
                                                    "border": "none",
                                                },
                                                style_cell={
                                                    "font-family": "sans-serif",
                                                    "white-space": "normal", # required for line breaks in utterance column
                                                    "padding": "15px",
                                                    "border": "1px solid #e9e9e9",   
                                                },
                                                css=[
                                                    # sum of absolute elements 30+38+30+52+15+38+15+72+15+250+15...+15+21+15
                                                    {"selector": ".dash-freeze-top",
                                                     "rule": "max-height: calc(100vh - 621px)"},
                                                    ],
                                                fixed_rows={"headers": True},
                                                page_action="none",
                                            ),
                                        ],
                                    ),
                                ],
                                ),
                                dbc.Tab(label="Wordcloud draft", children=[
                                    html.Div(style={"height": vertical_space}),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    html.H5("Parameters"),
                                                    dbc.Row(
                                                        [
                                                            dbc.Col(
                                                                [
                                                                    html.Div("Textblock length"),
                                                                    html.Div("in minutes"),
                                                                ],
                                                                width="auto",
                                                            ),
                                                            dbc.Col(
                                                                [
                                                                    dbc.Input(
                                                                        id="textblock_length_input",
                                                                        type="number",
                                                                        min=1,
                                                                        max=100,
                                                                        step=1,
                                                                        value=5,
                                                                    ),
                                                                ],
                                                                width="auto",
                                                            ),
                                                        ],
                                                    ),
                                                ],
                                                width="auto",
                                            ),
                                            dbc.Col(
                                                [
                                                    html.Div(style={"height": "27px"}),
                                                    dbc.Button(
                                                        "Apply",
                                                        id="apply_wordcloud_settings",
                                                        className="btn-outline-primary",
                                                    ),
                                                ],
                                                width="auto",
                                            ),

                                        ],
                                    ),
                                    html.Div(style={"height": vertical_space}),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    dcc.Graph(
                                                        id="wordcloud_plot",
                                                        figure={'layout': go.Layout(margin={'t': 0, "b":0, "r":0, "l":0})},
                                                        #config={"displayModeBar": False},
                                                        #style={"height": "600px"},
                                                    ),
                                                ],
                                            ),
                                            dbc.Col(
                                                [   
                                                    html.Div(
                                                        id = "vertical_slider",
                                                        style = {"visibility": "hidden"},
                                                        children = [
                                                            dcc.Slider(
                                                                id="wordcloud_steps_slider",
                                                                min=0,
                                                                max=9,
                                                                step = 1,
                                                                value = 9,
                                                                marks={},
                                                                vertical = True,        
                                                            ),
                                                        ],
                                                    ),  
                                                ], width=1,
                                            ),
                                        ],
                                    ),
                                ],
                                ),
                                dbc.Tab(label="Wordcloud animation", children=[
                                    html.Div(style={"height": vertical_space}),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    html.H5("Parameters"),
                                                    dbc.Row(
                                                        [
                                                            dbc.Col(
                                                                [
                                                                    html.Div("Textblock length"),
                                                                    html.Div("in minutes"),
                                                                ],
                                                                width="auto",
                                                            ),
                                                            dbc.Col(
                                                                [
                                                                    dbc.Input(
                                                                        id="textblock_length_input2",
                                                                        type="number",
                                                                        min=1,
                                                                        max=100,
                                                                        step=1,
                                                                        value=5,
                                                                    ),
                                                                ],
                                                                width="auto",
                                                            ),
                                                        ],
                                                    ),
                                                ],
                                                width="auto",
                                            ),
                                            dbc.Col(
                                                [
                                                    html.Div(style={"height": "27px"}),
                                                    dbc.Button(
                                                        "Apply",
                                                        id="apply_wordcloud_settings2",
                                                        className="btn-outline-primary",
                                                    ),
                                                ],
                                                width="auto",
                                            ),

                                        ],
                                    ),
                                    html.Div(style={"height": vertical_space}),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    dcc.Graph(
                                                        id="animation",
                                                        figure={'layout': go.Layout(margin={'t': 0, "b":0, "r":0, "l":0})},
                                                        config={"displayModeBar": False},
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                ],
                                ),
                                dbc.Tab(label="Wordcloud TF-IDF", children=[
                                    html.Div(style={"height": vertical_space}),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    html.H5("Parameters"),
                                                    dbc.Row(
                                                        [
                                                            dbc.Col(
                                                                [
                                                                    html.Div("Textblock length"),
                                                                    html.Div("in minutes"),
                                                                ],
                                                                width="auto",
                                                            ),
                                                            dbc.Col(
                                                                [
                                                                    dbc.Input(
                                                                        id="textblock_length_input3",
                                                                        type="number",
                                                                        min=1,
                                                                        max=100,
                                                                        step=1,
                                                                        value=5,
                                                                    ),
                                                                ],
                                                                width="auto",
                                                            ),
                                                        ],
                                                    ),
                                                ],
                                                width="auto",
                                            ),
                                            dbc.Col(
                                                [
                                                    html.Div(style={"height": "27px"}),
                                                    dbc.Button(
                                                        "Apply",
                                                        id="apply_wordcloud_settings3",
                                                        className="btn-outline-primary",
                                                    ),
                                                ],
                                                width="auto",
                                            ),

                                        ],
                                    ),
                                    html.Div(style={"height": vertical_space}),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    dcc.Graph(
                                                        id="animation_tfidf",
                                                        figure={'layout': go.Layout(margin={'t': 0, "b":0, "r":0, "l":0})},
                                                        config={"displayModeBar": False},
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                ],
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
        html.Div(style={"height": vertical_space}),
        html.Footer(
            id="footer",
            children=[
                html.Div("Pascal Aigner, Maurice Gerber, Basil Rohr | "),
                html.Div("ZHAW Zurich University of Applied Sciences | "),
                html.A("GitHub", href="https://github.com/pascalaigner/summarization", target="_blank"),
            ],
        ),
    ],
    fluid=True,
)

@app.callback(
    Output(component_id="transcript_selector", component_property="options"),
    Output(component_id="transcript_selector", component_property="value"),
    Output(component_id="modal", component_property="is_open"),
    Output(component_id="modal_header", component_property="children"),
    Output(component_id="modal_body", component_property="children"),
    Input(component_id="transcript_upload_button", component_property="contents"),
    Input(component_id="transcript_delete_button", component_property="n_clicks"),
    Input(component_id="modal_close_button", component_property="n_clicks"),
    State(component_id="transcript_selector", component_property="value"),
    State(component_id="transcript_upload_button", component_property="filename"),
    State(component_id="modal", component_property="is_open"),
)
def upload_and_delete_transcripts(list_of_contents, n_clicks_delete, n_clicks_modal,
                                  current_transcript, list_of_names, is_open):
    if is_open:
        return dash.no_update, dash.no_update, False, dash.no_update, dash.no_update

    trigger = dash.callback_context.triggered[0]["prop_id"]

    if trigger == "transcript_upload_button.contents":

        if list_of_contents is not None:
            content_type, content_string = list_of_contents.split(",")
            decoded = base64.b64decode(content_string)

            try:
                transcript = pd.read_csv(
                    filepath_or_buffer=io.StringIO(decoded.decode("utf-8")),
                    header=0,
                    names=["Speaker", "Time", "End time", "Duration", "Utterance"],
                    usecols=["Speaker", "Time", "Utterance"]
                )
                calculate_timestamps(transcript)
                transcripts.append(transcript)
                transcript_files.append(list_of_names)

                return ([{"label": transcript_files[i], "value": str(i)} for i in range(len(transcript_files))],
                        str(len(transcripts)-1), False, dash.no_update, dash.no_update)

            except Exception as e:
                return dash.no_update, dash.no_update, True, "An error occurred", str(e)

    if trigger == "transcript_delete_button.n_clicks":
        if len(transcript_files) > 1:
            transcript_files.pop(int(current_transcript))
            transcripts.pop(int(current_transcript))
            return ([{"label": transcript_files[i], "value": str(i)} for i in range(len(transcript_files))],
                    "0", False, dash.no_update, dash.no_update)
        else:
            return dash.no_update, dash.no_update, True, "An error occurred", "App must at least contain one transcript."
 
    return ([{"label": transcript_files[i], "value": str(i)} for i in range(len(transcript_files))],
            dash.no_update, False, dash.no_update, dash.no_update)

@app.callback(
    Output(component_id="transcript_table", component_property="data"),
    Output(component_id="transcript_table", component_property="css"),
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
    transcript = transcripts[int(selected_transcript)]

    timeline_min = transcript["Timestamp"][0]
    timeline_max = transcript["Timestamp"][len(transcript)-1]
    # difference between timeline_max and start of last minute, e.g. 44:21 - 44:00 = 00:21
    timeline_deviation = timeline_max - math.floor(timeline_max/60)*60
    marks = dict()

    trigger = dash.callback_context.triggered[0]["prop_id"]

    if trigger == "transcript_selector.value":
        speakers = transcript["Speaker"].unique()
        transcript_table = transcript[["Speaker", "Time", "Utterance"]].to_dict("records")

        # set height of transcript table depending on height of filter section
        if len(speakers) == 2:
            filter_section_height = 73
        elif len(speakers) == 3:
            filter_section_height = 90
        else:
            filter_section_height = 90 + (len(speakers)-3) * 21
        transcript_table_height = 30+38+30+52+15+38+15+filter_section_height+15+15+21+15
        css_code = "max-height: calc(100vh - " + str(transcript_table_height) + "px)"
        
        return (transcript_table, [{"selector": ".dash-freeze-top", "rule": css_code}],
                [{"label": i, "value": i} for i in sorted(speakers, key=str.lower)], speakers,
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
                first_timestamp = datetime.strptime("00:00", "%M:%S")
                current_start_time = datetime.strptime(selected_start_time, "%H:%M")
                current_end_time = datetime.strptime(selected_end_time, "%H:%M")
                # timeline_deviation is added to prevent last utterances from being filtered out
                # e.g. if 00:44 is entered, utterances from 00:44:01 to 00:44:21 would be filtered out if timeline_deviation was not added
                timeline_slider_values = [(current_start_time - first_timestamp).total_seconds(),
                                          (current_end_time - first_timestamp).total_seconds() + timeline_deviation]
                transcript = transcript[transcript["Timestamp"] >= timeline_slider_values[0]]
                transcript = transcript[transcript["Timestamp"] <= timeline_slider_values[1]]
                transcript_table = transcript[["Speaker", "Time", "Utterance"]].to_dict("records")

                return (transcript_table, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update,
                        dash.no_update, dash.no_update, timeline_slider_values, dash.no_update, dash.no_update)
            except:
                pass

        transcript = transcript[transcript["Timestamp"] >= selected_timeline[0]]
        transcript = transcript[transcript["Timestamp"] <= selected_timeline[1]]
        transcript_table = transcript[["Speaker", "Time", "Utterance"]].to_dict("records")

        return (transcript_table, dash.no_update, dash.no_update, dash.no_update,
                time.strftime("%H:%M", time.gmtime(selected_timeline[0])),
                time.strftime("%H:%M", time.gmtime(selected_timeline[1])),
                dash.no_update, dash.no_update, dash.no_update, marks, dash.no_update)

    return (dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update,
            dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update)

def build_download_button(uri):
    """Generates a download button for the resource"""
    button = html.Form(
        action=uri,
        method="get",
        target = "_blank",
        children=[
            dbc.Button(
                id = "pdf_download_button",
                className="btn-outline-primary",
                disabled = False,
                type="submit",
                children=["download"]
            )
        ]
    )
    return button

@app.callback(
    Output(component_id="download-area", component_property="children"),
    Output(component_id="pdf_download_button", component_property="className"),
    Output(component_id="pdf_download_button", component_property="disabled"),
    Input(component_id="pdf_generate_button", component_property="n_clicks"),
    Input(component_id="transcript_table", component_property="data")
)

def pdf_generate(n_clicks, current_transcript):
    trigger = dash.callback_context.triggered[0]["prop_id"]
    if trigger == "pdf_generate_button.n_clicks":
        transcript = pd.DataFrame.from_records(current_transcript)
        uri = create_pdf.create_pdf(transcript)
        return [build_download_button(uri)], dash.no_update, False
    return dash.no_update, "btn-secondary disabled", True

@app.server.route('/downloadable/<path:path>')
def serve_static(path):
    return flask.send_from_directory(
        os.path.join(".", 'downloadable'), path
    )

@app.callback(
    Output(component_id="texttiling_plot", component_property="figure"),
    Output(component_id="texttiling_table", component_property="data"),
    Input(component_id="apply_texttiling_settings", component_property="n_clicks"),
    State(component_id="transcript_selector", component_property="value"),
    State(component_id="language_radio_button", component_property="value"),
    State(component_id="stopwords_input", component_property="value"),
    State(component_id="pseudosentence_length_input", component_property="value"),
    State(component_id="block_size_input", component_property="value"),
    State(component_id="n_topics_input", component_property="value"),
)
def apply_texttiling(n_clicks, selected_transcript, selected_language, additional_stopwords,
                     pseudosentence_length, block_size, n_topics):
    if dash.callback_context.triggered[0]["prop_id"] == "apply_texttiling_settings.n_clicks":
        transcript = transcripts[int(selected_transcript)]

        additional_stopwords_list = []
        if additional_stopwords != None:
            additional_stopwords_list = additional_stopwords.split(",")
        sw = set(stopwords.words(selected_language) + additional_stopwords_list)
        
        normalized_boundaries, boundaries, depth_scores = texttiling.texttiling(transcript, sw, pseudosentence_length,
                                                                                block_size, n_topics)
        boundaries_timestamps = [transcript["Timestamp"][i] for i in normalized_boundaries]
        boundaries_time = [transcript["Time"][normalized_boundaries[i-1]] + " - " + transcript["Time"][normalized_boundaries[i]]
                           for i in range(1, len(normalized_boundaries))]
        
        subtopics = []
        for i in range(1, len(boundaries_timestamps)):
            transcript_subtopic = transcript[transcript["Timestamp"] < boundaries_timestamps[i]]
            transcript_subtopic = transcript_subtopic[transcript_subtopic["Timestamp"] >= boundaries_timestamps[i-1]]
            text = ""
            for utterance in transcript_subtopic["Utterance"].str.lower():
                text += utterance
            subtopics.append(text)
            
        df = tfidf.tfidf(subtopics)
        keywords = []
        for column in df:
            keywords.append(", ".join(list(df[column].sort_values(ascending=False).index[:10])))
        
        data = {"Start time": boundaries_time, "Keywords": keywords}
        keywords_table = pd.DataFrame(data=data).to_dict("records")

        fig = go.Figure()
        fig["layout"] = go.Layout(margin={"t": 0, "b": 0, "r": 0, "l": 0})
        for i in range(len(boundaries)):
            fig.add_shape(
                type="line",
                x0=boundaries[i],
                y0=0,
                x1=boundaries[i],
                y1=max(depth_scores),
                line=dict(
                    color="DarkOrange",
                    width=3,
                    dash="dot",
            ))
            fig.add_annotation(
                x=boundaries[i],
                y=max(depth_scores)+0.03,
                text=transcript["Time"][normalized_boundaries[i+1]],
                showarrow=False,
            )
        fig.add_trace(go.Scatter(
            x=list(range(len(depth_scores))),
            y=depth_scores,
            mode="lines"
        ))
        fig.update_layout(
            xaxis_title="Gap between pseudosentences",
            yaxis_title="Depth score",
        )

        return fig, keywords_table

    return dash.no_update, dash.no_update

@app.callback(
    Output(component_id="wordcloud_plot", component_property="figure"),
    Output(component_id="vertical_slider", component_property="style"),
    Output(component_id="wordcloud_steps_slider", component_property="max"),
    Output(component_id="wordcloud_steps_slider", component_property="value"),
    Output(component_id="wordcloud_steps_slider", component_property="marks"),
    Input(component_id="apply_wordcloud_settings", component_property="n_clicks"),
    Input(component_id="transcript_selector", component_property="value"),
    Input(component_id="wordcloud_steps_slider", component_property="value"),
    Input(component_id="textblock_length_input", component_property="value"),
)
def wordcloud_creator(n_clicks, selected_transcript, section, slct_min):
    
    if dash.callback_context.triggered[0]["prop_id"] == "apply_wordcloud_settings.n_clicks":
        transcript = transcripts[int(selected_transcript)]
        data = transcript.to_dict("records")

        words, min_seq, counts = split_dialog.split_dialog(data, slct_min)
        
        min_rev = list(min_seq)[::-1]
        marks={i-1: str(min_rev[i])+"-"+str(min_rev[i-1])+" min" for i in range(1,len(min_seq))}
        
        max_section = len(words)-1
        current_section = max_section
        
        dict_selected = words[0]
        ldict = len(dict_selected)
        
        fig = wordcloud_pl.plot(dict_selected, ldict)
        
        return fig, {"visibility": "visible"}, max_section, current_section, marks
    

    if dash.callback_context.triggered[0]["prop_id"] == "wordcloud_steps_slider.value":    
        transcript = transcripts[int(selected_transcript)]
        data = transcript.to_dict("records")

        words, min_seq, counts = split_dialog.split_dialog(data, slct_min)

        max_section = len(words)-1
        current_section = abs(section - max_section)
        
        dict_selected = words[current_section]
        ldict = len(dict_selected)

        fig = wordcloud_pl.plot(dict_selected, ldict)

        return fig, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

@app.callback(
    Output(component_id="animation", component_property="figure"),
    Input(component_id="apply_wordcloud_settings2", component_property="n_clicks"),
    State(component_id="transcript_selector", component_property="value"),
    State(component_id="textblock_length_input2", component_property="value"),
)
def animation2(n_clicks, selected_transcript, slct_min):

    if dash.callback_context.triggered[0]["prop_id"] == "apply_wordcloud_settings2.n_clicks":
        transcript = transcripts[int(selected_transcript)]
        data = transcript.to_dict("records")
        words, min_seq, word_counts = split_dialog.split_dialog(data, slct_min)

        for word, counts in word_counts.copy().items():
            if sum(counts) <= len(min_seq):
                del word_counts[word]

        number_of_words = len(word_counts)

        random.x = random.sample(range(number_of_words), number_of_words)
        random.y = random.sample(range(number_of_words), number_of_words)

        grid_width = math.ceil(math.sqrt(number_of_words))
        grid_x = []
        grid_y = []

        for x in range(0,grid_width*4, 4):
            for y in range(grid_width):
                grid_x.append(x)
                grid_y.append(y)

        grid_x = grid_x[:number_of_words]
        grid_y = grid_y[:number_of_words]

        iteration_counter = 0
       
        word_col = []
        block_col = []
        count_col = []
        gridx_col =[]
        gridy_col = []
        for word, counts in word_counts.items():
            for i in range(len(counts)):
                word_col.append(word)
                block_col.append(i)
                count_col.append(counts[i])
                gridx_col.append(grid_x[iteration_counter])
                gridy_col.append(grid_y[iteration_counter])
            iteration_counter += 1
        df = pd.DataFrame({'word': word_col, 'block': block_col, 'count': count_col, 'x': gridx_col, 'y': gridy_col})

        scaler = MinMaxScaler(feature_range=(1, 60))
        df["marker_size"] = scaler.fit_transform(df["count"].values.reshape(-1,1))

        scaler2 = MinMaxScaler()
        df["opacity"] = scaler2.fit_transform(df["count"].values.reshape(-1,1))

        # filtered_data = df[df["word"]=="plan"]
        # print(filtered_data)

        blocks = df["block"].unique().tolist()

        # make figure
        fig_dict = {
            "data": [],
            "layout": {},
            "frames": []
        }

        # fill in most of layout
        fig_dict["layout"] = go.Layout(margin={'t': 0, "b":0, "r":0, "l":0}, plot_bgcolor="rgba(0,0,0,0)")
        fig_dict["layout"]["xaxis"] = {"title": "x", "showgrid": False, 'zeroline': False, 'visible': False}
        fig_dict["layout"]["yaxis"] = {"title": "y", "showgrid": False, 'zeroline': False, 'visible': False}
        fig_dict["layout"]["hovermode"] = "closest"
        fig_dict["layout"]["updatemenus"] = [
            {
                "buttons": [
                    {
                        "args": [None, {"frame": {"duration": 2000, "redraw": False},
                                        "fromcurrent": True,
                                        "transition": {"duration": 1000, "easing": "linear"} # animation when clicking play
                                        }],
                        "label": "Play",
                        "method": "animate"
                    },
                    {
                        "args": [[None], {"frame": {"duration": 0, "redraw": False},
                                        "mode": "immediate",
                                        "transition": {"duration": 0}
                                        }],
                        "label": "Pause",
                        "method": "animate"
                    }
                ],
                "direction": "left",
                "pad": {"r": 10, "t": 87},
                "showactive": False,
                "type": "buttons",
                "x": 0.1,
                "xanchor": "right",
                "y": 0,
                "yanchor": "top"
            }
        ]

        sliders_dict = {
            "active": 0,
            "yanchor": "top",
            "xanchor": "left",
            "currentvalue": {
                "font": {"size": 20},
                "prefix": "Text block:",
                "visible": True,
                "xanchor": "right"
            },
            "transition": {"duration": 400, "easing": "linear"},
            "pad": {"b": 10, "t": 50},
            "len": 0.9,
            "x": 0.1,
            "y": 0,
            "steps": []
        }

        # make data
        block = blocks[0]
        dataset_by_block = df[df["block"] == block]

        data_dict = {
            "x": list(dataset_by_block["x"]),
            "y": list(dataset_by_block["y"]),
            "mode": "text + markers",
            "text": list(dataset_by_block["word"]),
            "textfont": dict(size = list(dataset_by_block["marker_size"])),
            "marker": {
                "sizemode": "area",
                "sizeref": 0.01,
                "opacity": list(dataset_by_block["opacity"]),
                "size": list(dataset_by_block["marker_size"]),
            },
        }
        fig_dict["data"].append(data_dict)

        for block in blocks:
            frame = {"data": [], "name": str(block)}
            dataset_by_block = df[df["block"] == block]

            data_dict = {
                "x": list(dataset_by_block["x"]),
                "y": list(dataset_by_block["y"]),
                "mode": "text + markers",
                "text": list(dataset_by_block["word"]),
                "textfont": dict(size = list(dataset_by_block["marker_size"])),
                "marker": {
                    "sizemode": "area",
                    "sizeref": 0.01,
                    "opacity": list(dataset_by_block["opacity"]),
                    "size": list(dataset_by_block["marker_size"])
                },
            }
            frame["data"].append(data_dict)

            fig_dict["frames"].append(frame)
            slider_step = {"args": [
                [block],
                {"frame": {"duration": 0, "redraw": False},
                "mode": "immediate",
                "transition": {"duration": 0}}
            ],
                "label": block,
                "method": "animate"}
            sliders_dict["steps"].append(slider_step)

        fig_dict["layout"]["sliders"] = [sliders_dict]

        fig = go.Figure(fig_dict)
        fig.update_yaxes(scaleanchor = "x", scaleratio = 1)

        return fig

    return dash.no_update


@app.callback(
    Output(component_id="animation_tfidf", component_property="figure"),
    Input(component_id="apply_wordcloud_settings3", component_property="n_clicks"),
    State(component_id="transcript_selector", component_property="value"),
    State(component_id="textblock_length_input3", component_property="value"),
)

def animation_tfidf(n_clicks, selected_transcript, slct_min):
    if dash.callback_context.triggered[0]["prop_id"] == "apply_wordcloud_settings3.n_clicks":
        transcript = transcripts[int(selected_transcript)]
        data = transcript.to_dict("records")
        tf_dict, idf_dict, tfidf_dict, min_seq = tf_idf.tf_idf(data, slct_min)

        number_of_words = len(tfidf_dict)
        
        iteration_counter = 0
        word_col = []
        block_col = []
        tf_col =[]
        idf_col = []
        tfidf_col = []
        for word, counts in tfidf_dict.items():
            for i in range(len(counts)):
                if sum(counts) > 0.001:
                    word_col.append(word)
                    block_col.append(i+1)
                    tf_col.append(tf_dict[word][i])
                    idf_col.append(idf_dict[word][0])
                    tfidf_col.append(counts[i])
            iteration_counter += 1
        df = pd.DataFrame({'word': word_col, 'block': block_col, 'x': tf_col, 'y': idf_col, 'score': tfidf_col})
        print(df)
        # pd.set_option("display.max_rows", None, "display.max_columns", None)
        # print(df)
        blocks = df["block"].unique().tolist()

        num_blocks = range(1,len(min_seq))
        max_block = len(min_seq)-1
        y_tickvals_range = list(num_blocks)[:-1]
        y_tickvals_range.reverse()
        
        y_tickvals = [math.log(max_block / x) for x in y_tickvals_range]
        y_ticktext = [str(x) + "/" + str(max_block) for x in y_tickvals_range]

        # make figure
        fig_dict = {
            "data": [],
            "layout": {},
            "frames": []
        }

        # fill in most of layout
        fig_dict["layout"] = go.Layout(margin={'t': 0, "b":0, "r":0, "l":0}, plot_bgcolor="rgba(0,0,0,0)")
        fig_dict["layout"]["xaxis"] = {"title": "Frequency in Block", "showgrid": True, 'zeroline': True, 'visible': True, "range": [-0.001,0.014]}
        fig_dict["layout"]["yaxis"] = {"title": "Inverse Document Frequency", "showgrid": True, 'zeroline': True, 'visible': True, "tickmode": "array", "tickvals": y_tickvals,
        "ticktext": y_ticktext, "type": "log"}
        fig_dict["layout"]["hovermode"] = "closest"
        fig_dict["layout"]["updatemenus"] = [
            {
                "buttons": [
                    {
                        "args": [None, {"frame": {"duration": 2000, "redraw": False},
                                        "fromcurrent": True,
                                        "transition": {"duration": 1000, "easing": "linear"} # animation when clicking play
                                        }],
                        "label": "Play",
                        "method": "animate"
                    },
                    {
                        "args": [[None], {"frame": {"duration": 0, "redraw": False},
                                        "mode": "immediate",
                                        "transition": {"duration": 0}
                                        }],
                        "label": "Pause",
                        "method": "animate"
                    }
                ],
                "direction": "left",
                "pad": {"r": 10, "t": 87},
                "showactive": False,
                "type": "buttons",
                "x": 0.1,
                "xanchor": "right",
                "y": 0,
                "yanchor": "top"
            }
        ]

        sliders_dict = {
            "active": 0,
            "yanchor": "top",
            "xanchor": "left",
            "currentvalue": {
                "font": {"size": 20},
                "prefix": "Text block:",
                "visible": True,
                "xanchor": "right"
            },
            "transition": {"duration": 400, "easing": "linear"},
            "pad": {"b": 10, "t": 50},
            "len": 0.9,
            "x": 0.1,
            "y": 0,
            "steps": []
        }

        # make data
        block = blocks[0]
        dataset_by_block = df[df["block"] == block]

        data_dict = {
            "x": list(dataset_by_block["x"]),
            "y": list(dataset_by_block["y"]),
            "mode": "text",
            "text": list(dataset_by_block["word"]),
            "marker": {
                "sizemode": "area",
                "sizeref": 0.01
            },
            "customdata": dataset_by_block["score"],
            "hovertemplate": '%{text}<br>TF-Score: %{x:.3f}<br>IDF-Score: %{y:.3f}<br>TF-IDF-Score: %{customdata:.3f}<extra></extra>'
        }
        fig_dict["data"].append(data_dict)

        for block in blocks:
            frame = {"data": [], "name": str(block)}
            dataset_by_block = df[df["block"] == block]

            data_dict = {
                "x": list(dataset_by_block["x"]),
                "y": list(dataset_by_block["y"]),
                "mode": "text",
                "text": list(dataset_by_block["word"]),
                "marker": {
                    "sizemode": "area",
                    "sizeref": 0.01
                },
                "customdata": dataset_by_block["score"],
                "hovertemplate": '%{text}<br>TF-Score: %{x:.3f}<br>IDF-Score: %{y:.3f}<br>TF-IDF-Score: %{customdata:.3f}<extra></extra>'
            }
            frame["data"].append(data_dict)

            fig_dict["frames"].append(frame)
            slider_step = {"args": [
                [block],
                {"frame": {"duration": 0, "redraw": False},
                "mode": "immediate",
                "transition": {"duration": 0}}
            ],
                "label": block,
                "method": "animate"}
            sliders_dict["steps"].append(slider_step)

        fig_dict["layout"]["sliders"] = [sliders_dict]

        fig = go.Figure(fig_dict)
        return fig
        
    return dash.no_update



if __name__ == "__main__":
    # context = ("/etc/letsencrypt/live/projects.pascalaigner.ch/cert.pem", "/etc/letsencrypt/live/projects.pascalaigner.ch/privkey.pem")
    app.run_server(
        # host="projects.pascalaigner.ch",
        # port=443,
        # ssl_context=context,
        debug=True)