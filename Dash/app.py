import os
import pandas as pd

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

# import tabs
from tabs.tab_transcript import tab_transcript
from tabs.tab_keywords import tab_keywords
from tabs.tab_texttiling import tab_texttiling
from tabs.tab_textsplit import tab_textsplit
from tabs.tab_wordcloud_draft import tab_wordcloud_draft
from tabs.tab_wordcloud_animation import tab_wordcloud_animation
from tabs.tab_wordcloud_tfidf import tab_wordcloud_tfidf
from tabs.tab_wordcloud_tfidf2 import tab_wordcloud_tfidf2

# import callbacks
from callbacks.callback_upload_and_delete_transcripts import callback_upload_and_delete_transcripts
from callbacks.callback_update_transcript_table_and_filters import callback_update_transcript_table_and_filters
from callbacks.callback_create_and_download_pdf import callback_create_and_download_pdf
from callbacks.callback_apply_texttiling import callback_apply_texttiling
from callbacks.callback_apply_textsplit import callback_apply_textsplit
from callbacks.callback_wordcloud_creator import callback_wordcloud_creator
from callbacks.callback_animation import callback_animation
from callbacks.callback_animation_tfidf import callback_animation_tfidf

# import functions
from functions.calculate_timestamps import calculate_timestamps

# theme https://bootswatch.com/lux/
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
                                tab_transcript(initial_transcript, initial_timeline_min, initial_timeline_max),
                                tab_keywords(),
                                tab_texttiling(),
                                tab_textsplit(),
                                tab_wordcloud_draft(),
                                tab_wordcloud_animation(),
                                tab_wordcloud_tfidf(),
                                tab_wordcloud_tfidf2(),
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

callback_upload_and_delete_transcripts(app, transcript_files, transcripts)

callback_update_transcript_table_and_filters(app, transcripts)

callback_create_and_download_pdf(app)

callback_apply_texttiling(app, transcripts)

callback_apply_textsplit(app, transcripts)

callback_wordcloud_creator(app, transcripts)

callback_animation(app, transcripts)

callback_animation_tfidf(app, transcripts)

if __name__ == "__main__":
    # context = (
    #     "/etc/letsencrypt/live/projects.pascalaigner.ch/cert.pem",
    #     "/etc/letsencrypt/live/projects.pascalaigner.ch/privkey.pem"
    # )
    app.run_server(
        # host="projects.pascalaigner.ch",
        # port=443,
        # ssl_context=context,
        debug=True
    )