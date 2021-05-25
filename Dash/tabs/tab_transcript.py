import time

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table

def tab_transcript(initial_transcript, initial_timeline_min, initial_timeline_max):
    vertical_space = "15px"
    tab = dbc.Tab(label="Transcript", children=[
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
    )
    return tab