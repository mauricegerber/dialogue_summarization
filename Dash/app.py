import os
import sys
import pandas as pd
from datetime import datetime
import time

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import dash_table

import plotly.graph_objects as go

from nltk.corpus import stopwords
from sklearn.preprocessing import MinMaxScaler

sys.path.insert(0, "./lib")
import calculate_timestamps
import upload_and_delete_transcripts_callback
import pdf_callback
import transcript_table_callback
import texttiling_callback
import textsplit_callback
import wordcloud_creator_callback
import animation_callback
import animation_tfidf_callback

# https://bootswatch.com/lux/
BS = "https://stackpath.bootstrapcdn.com/bootswatch/4.5.2/lux/bootstrap.min.css"
app = dash.Dash(external_stylesheets=[BS])
app.title = "Dialog Analyzer"

transcripts_dir = "./transcripts/"
transcript_files = os.listdir(transcripts_dir)
initial_transcript_index = 0

transcripts = []
for file in transcript_files:
    transcript = pd.read_csv(
        filepath_or_buffer=transcripts_dir + file,
        header=0,
        names=["Speaker", "Time", "End time", "Duration", "Utterance"],
        usecols=["Speaker", "Time", "Utterance"]
    )
    calculate_timestamps.calculate_timestamps(transcript)
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
                                    disabled = True,
                                ),
                            ],
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
                                            {"name": "Utterance", "id": "Utterance", "presentation": "markdown"},
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
                                dbc.Tab(label="Keyword extraction", children=[
                                    html.Div(style={"height": vertical_space}),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    html.Div(
                                                        children=[
                                                            html.Span("This tab provides implementations of several keyword extraction algorithms."),
                                                            html.Span(" The keywords are displayed in the table in Tab 1."),
                                                            html.Span(" As this tab is quite empty at the moment, more information or settings might get added."),
                                                            html.Span(" Note that KeyBERT takes quite a while to compute compared to the others.")

                                                        ],
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                    html.Div(style={"height": vertical_space}),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    dbc.Checklist(
                                                        id="keyword_extraction_method_selector",
                                                        options=[
                                                            {"label": "TF-IDF", "value": "tf-idf"},
                                                            {"label": "TextRank", "value": "textrank"},
                                                            {"label": "YAKE!", "value": "yake"},
                                                            {"label": "BERT", "value": "bert"},
                                                        ],
                                                        value=[],
                                                        switch=True,
                                                    ),
                                                ],
                                                width="auto",
                                            ),
                                            dbc.Col(
                                                [
                                                    html.Div(style={"height": "27px"}),
                                                    dbc.Button(
                                                        "Apply",
                                                        id="apply_keyword_extraction_settings",
                                                        className="btn-outline-primary",
                                                    ),
                                                ],
                                                width="auto",
                                            ),
                                        ],
                                    ),
                                ],
                                ),
                                dbc.Tab(label="TextTiling", children=[
                                    html.Div(style={"height": vertical_space}),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    html.Div(
                                                        children=[
                                                            html.Span("This tab provides an implementation of the TextTiling algorithm proposed by Marti A. Hearst "),
                                                            html.A("[Link to paper].", href="https://www.aclweb.org/anthology/J97-1003.pdf", target="_blank"),
                                                            html.Span(" The cues for detecting major subtopic shifts are patterns of lexical co-occurrence."),
                                                            html.Span(" The radio button"),
                                                            html.I(" Language"),
                                                            html.Span(" is to set the list of stop words to the corresponding language."),
                                                            html.Span(" Additional stop words can be provided."),
                                                            html.Span(" Stop words only affect the TextTiling algorithm and not the tf-idf keyword extraction."),
                                                            html.Span(" The parameters"),
                                                            html.I(" Pseudeosentence length w"),
                                                            html.Span(","),
                                                            html.I(" Block size k"),
                                                            html.Span(" and"),
                                                            html.I(" Number of subtopics n"),
                                                            html.Span(" can be adjusted to fine-tune the TextTiling algorithm."),
                                                            html.Span(" For a detailed discussion on the effects of these parameters please refer to chapter X in our paper [link not yet available]."),
                                                        ],
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
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
                                                    # sum of absolute elements 30+38+30+52+15+38+15+63+15+72+15+250+15...+15+21+15
                                                    {"selector": ".dash-freeze-top",
                                                     "rule": "max-height: calc(100vh - 699px)"},
                                                    ],
                                                fixed_rows={"headers": True},
                                                page_action="none",
                                            ),
                                        ],
                                    ),
                                ],
                                ),
                                dbc.Tab(label="TextSplit", children=[
                                    html.Div(style={"height": vertical_space}),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    html.Div(
                                                        children=[
                                                            html.Span("This tab provides an implementation of a text split algorithm by Christoph Schock "),
                                                            html.A("[Link to GitHub]", href="https://github.com/chschock/textsplit", target="_blank"),
                                                            html.Span(" which is based on a paper by Alexander A. Alemi and Paul Ginsparg "),
                                                            html.A("[Link to paper].", href="https://arxiv.org/pdf/1503.05543.pdf", target="_blank"),
                                                            html.Span(" The algorithm uses word embeddings to find subtopics where the boundaries are chosen such that the subtopics are coherent."),
                                                            html.Span(" This coherence can be described as accumulated weighted cosine similarity of the words of a subtopic to the mean vector of that subtopic."),
                                                            html.Span(" The parameter"),
                                                            html.I(" Segment length"),
                                                            html.Span(" can be adjusted to fine-tune the algorithm and affect the number of subtopics it detects."),
                                                            html.Span(" For a detailed discussion of the algorithm please refer to chapter X in our paper [link not yet available]."),
                                                        ],
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
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
                                                                    html.Div("Segment length"),
                                                                ],
                                                                width="auto",
                                                            ),
                                                            dbc.Col(
                                                                [
                                                                    dbc.Input(
                                                                        id="segment_length_input",
                                                                        type="number",
                                                                        step=1,
                                                                        value=30,
                                                                    ),
                                                                ],
                                                                width="auto",
                                                            ),
                                                        ],
                                                    ),
                                                ],
                                                width="auto",
                                                #style={"margin": "0% 3% 0% 0%"},
                                            ),
                                            dbc.Col(
                                                [
                                                    html.Div(style={"height": "27px"}),
                                                    dbc.Button(
                                                        "Apply",
                                                        id="apply_textsplit_settings",
                                                        className="btn-outline-primary",
                                                    ),
                                                ],
                                                width="auto",
                                            ),
                                        ],
                                    ),
                                    html.Div(style={"height": vertical_space}),
                                    dcc.Loading(
                                        id="loading2",
                                        color="#1a1a1a",
                                        children=[
                                            dcc.Graph(
                                                id="textsplit_plot",
                                                figure={"layout": go.Layout(margin={"t": 0, "b": 0, "r": 0, "l": 0})},
                                                config={"displayModeBar": False},
                                                style={"height": "250px"},
                                            ),
                                            html.Div(style={"height": vertical_space}),
                                            dash_table.DataTable(
                                                id="textsplit_table",
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
                                                    # sum of absolute elements 30+38+30+52+15+38+15+63+15+72+15+250+15...+15+21+15
                                                    {"selector": ".dash-freeze-top",
                                                     "rule": "max-height: calc(100vh - 699px)"},
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

upload_and_delete_transcripts_callback.upload_and_delete_transcripts(app, transcript_files, transcripts)

transcript_table_callback.transcript_table_callback(app, transcripts)

pdf_callback.create_and_download_pdf(app)

texttiling_callback.texttiling_callback(app, transcripts)

textsplit_callback.textsplit_callback(app, transcripts)

wordcloud_creator_callback.wordcloud_creator(app, transcripts)

animation_callback.animation(app, transcripts)

animation_tfidf_callback.animation_tfidf(app, transcripts)

if __name__ == "__main__":
    # context = ("/etc/letsencrypt/live/projects.pascalaigner.ch/cert.pem", "/etc/letsencrypt/live/projects.pascalaigner.ch/privkey.pem")
    app.run_server(
        # host="projects.pascalaigner.ch",
        # port=443,
        # ssl_context=context,
        debug=True)