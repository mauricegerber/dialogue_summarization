import os
import pandas as pd
from datetime import datetime
import time
import base64
import io

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import dash_table

import plotly.express as px
import plotly.graph_objects as go

from summa import keywords
# from pytopicrank import TopicRank

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
transcripts_files = os.listdir(transcripts_dir)
initial_transcript_index = 1

transcripts = []
for file in transcripts_files:
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
initial_timeline_max = initial_transcript["Timestamp"][initial_transcript.index[-1]]

app.layout = dbc.Container(
    [
        html.Br(),
        html.H1("Dialog analyzer"),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Select(
                            id="transcript_selector",
                            options=[{"label": transcripts_files[i], "value": i} for i in range(len(transcripts_files))],
                            value=initial_transcript_index,
                        ),
                    ],
                    width=3,
                ),
                dbc.Col(
                    [
                        dcc.Upload(children = [dbc.Button("Upload")], id = "upload_input"),
                        html.Div(id="output-data-upload", children = []),
                    
                    ],
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
                                dbc.Tab(label="Transcript", id="transcript_tab", children=[
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    html.Br(),
                                                    html.H5("Select speaker"),
                                                    dbc.Checklist(
                                                        id="speaker_selector",
                                                        options=[{"label": i, "value": i}
                                                                 for i in sorted(initial_transcript["Speaker"].unique(),
                                                                 key=str.lower)],
                                                        value=initial_transcript["Speaker"].unique(),
                                                    ),
                                                ],
                                                width=2,
                                            ),
                                            dbc.Col(
                                                [
                                                    html.Br(),
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
                                                                width="100px",
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
                                                                width=9,
                                                            ),
                                                            dbc.Col(
                                                                [
                                                                    dbc.Input(
                                                                        id="end_time_input",
                                                                        type="time",
                                                                        value=time.strftime("%H:%M",
                                                                                            time.gmtime(initial_timeline_max)),
                                                                    ),
                                                                ],
                                                                width="100px",
                                                            ),
                                                        ],
                                                    ),  
                                                ],
                                                width=8,
                                            ),
                                            dbc.Col(
                                                [
                                                    html.Br(),
                                                    html.H5("Search"),
                                                    dbc.Input(
                                                        id="search_input",
                                                        type="search",
                                                        placeholder="Enter search term here",
                                                    ),
                                                ],
                                                width=2,
                                            ),
                                        ],
                                    ),
                                    html.Br(),
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
                                dbc.Tab(label="Keywords", id="keywords_tab", children=[
                                    dcc.Graph(id="keywords_plot", figure={}),
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
    transcript = transcripts[int(selected_transcript)]

    timeline_min = transcript["Timestamp"][0]
    timeline_max = transcript["Timestamp"][transcript.index[-1]]
    timeline_deviation = timeline_max - int(timeline_max/60)*60

    trigger = dash.callback_context.triggered[0]["prop_id"]

    if trigger == "transcript_selector.value":
        speakers = transcript["Speaker"].unique()
        transcript_table = transcript[["Speaker", "Time", "Utterance"]].to_dict("records")
        
        return (transcript_table, [{"label": i, "value": i} for i in sorted(speakers, key=str.lower)], speakers,
                "00:00", time.strftime("%H:%M", time.gmtime(timeline_max)),
                timeline_min, timeline_max, [timeline_min, timeline_max], dict(), None)
    
    if trigger != "." and trigger != "transcript_selector.value":
        marks = dict()
        transcript = transcript[transcript["Speaker"].isin(selected_speaker)]
        
        if search_term != None and len(search_term) > 1:
            transcript = transcript[transcript["Utterance"].str.contains(search_term, case=False, regex=False)]
            if search_term[-1] == " ":
                transcript["Utterance"] = transcript["Utterance"].str.replace(search_term[:-1], "**" + search_term[:-1] + "**", case=False)
            else:
                transcript["Utterance"] = transcript["Utterance"].str.replace(search_term, "**" + search_term + "**", case=False)
            mark_symbol = ["|"] * len(transcript)
            marks = dict(zip(transcript["Timestamp"], mark_symbol))

        if trigger == "start_time_input.value" or trigger == "end_time_input.value":
            first_timestamp = datetime.strptime("0:00", "%M:%S")
            current_start_time = datetime.strptime(selected_start_time, "%H:%M")
            current_end_time = datetime.strptime(selected_end_time, "%H:%M")
            timeline_slider_values = [(current_start_time - first_timestamp).total_seconds(),
                                      (current_end_time - first_timestamp).total_seconds() + timeline_deviation]
            transcript = transcript[transcript["Timestamp"] >= timeline_slider_values[0]]
            transcript = transcript[transcript["Timestamp"] <= timeline_slider_values[1]]
            transcript_table = transcript[["Speaker", "Time", "Utterance"]].to_dict("records")
            
            return (transcript_table, dash.no_update, dash.no_update, dash.no_update, dash.no_update,
                    dash.no_update, dash.no_update, timeline_slider_values, marks, dash.no_update)

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
    Input(component_id="transcript_selector", component_property="value"),
)
def create_keywords_plot(selected_transcript):
    transcript = transcripts[int(selected_transcript)]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=[1, 2, 3],
        y=[1, 4, 9],
        mode="text",
        name="Lines, Markers and Text",
        text=["Text A", "Text B", "Text C"],
        textposition="middle center"
    ))

    # x = [0, 1, 2, 3, 4]
    # y = [0, 1, 4, 9, 16]
    # w = ["one", "two", "three", "four", "five"]
    # fig = px.scatter(x=x, y=y, text=w)
    
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
        print(e)
        return html.Div(['There was an error processing this file.'])
        
    return df


@app.callback(
    Output(component_id="transcript_selector", component_property="options"),
    Input(component_id="upload_input", component_property="contents"),
    State(component_id="upload_input", component_property="filename"),
    State(component_id="upload_input", component_property="last_modified"))


def update_transcripts(list_of_contents, list_of_names, list_of_dates):  
    if list_of_contents is not None:

        transcript = parse_contents(list_of_contents, list_of_names, list_of_dates)
        
        transcript["Time"] = transcript["Time"].str.replace("60", "59")
        calculate_timestamps(transcript)
        
        transcripts.append(transcript)
        transcripts_files.append(list_of_names)
        return [{"label": transcripts_files[i], "value": i} for i in range(len(transcripts_files))]

    return dash.no_update






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
    app.run_server(debug=True)
