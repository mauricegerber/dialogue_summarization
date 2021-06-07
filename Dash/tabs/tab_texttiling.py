import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table

import plotly.graph_objects as go

def tab_texttiling():
    vertical_space = "15px"
    tab = dbc.Tab(label="TextTiling", children=[
        html.Div(style={"height": vertical_space}),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            children=[
                                html.Span("This tab provides an implementation of the TextTiling algorithm proposed by Marti Hearst in 1997 "),
                                html.A("[Link to paper]", href="https://www.aclweb.org/anthology/J97-1003.pdf", target="_blank"),
                                html.Span(". The cues for detecting major subtopic shifts are patterns of lexical co-occurrence."),
                                html.Span(" For an explanation of the algorithm and its parameters we refer to our paper."),
                                html.Span(" Note that when clicking"),
                                html.I(" Apply"),
                                html.Span(", the keyword extraction settings from tab 2 are used to display the keywords table."),
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
                                        html.Div("Pseudosentence"),
                                        html.Div("length"),
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
                                        html.Div("Block size"),
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
                                        html.Div("subtopics"),
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
                        {"name": "Keywords", "id": "Keywords", "presentation": "markdown"},
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
    )
    return tab