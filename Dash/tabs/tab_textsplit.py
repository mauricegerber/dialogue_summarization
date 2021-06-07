import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table

import plotly.graph_objects as go

def tab_textsplit():
    vertical_space = "15px"
    tab = dbc.Tab(label="Textsplit", children=[
        html.Div(style={"height": vertical_space}),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            children=[
                                html.Span("This tab provides an implementation of the textsplit algorithm developed by Christoph Schock in 2020 "),
                                html.A("[Link to GitHub]", href="https://github.com/chschock/textsplit", target="_blank"),
                                html.Span(" which is based on a paper by Alexander Alemi and Paul Ginsparg from 2015 "),
                                html.A("[Link to paper]", href="https://arxiv.org/pdf/1503.05543.pdf", target="_blank"),
                                html.Span(". The algorithm uses word embedding and similarity measures to determine subtopics."),
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
                        html.H5("Break condition"),
                        dbc.RadioItems(
                            id="break_condition_radio_button",
                            options=[
                                {"label": "Number of subtopics", "value": "max_splits"},
                                {"label": "Min gain", "value": "min_gain"},
                            ],
                            value="max_splits",
                        ),
                    ],
                    width="auto",
                ),
                dbc.Col(
                    [
                        html.H5("Parameters"),
                        dbc.Row(
                            [
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
                                            id="max_splits_input",
                                            type="number",
                                            step=1,
                                            value=3,
                                        ),
                                    ],
                                    width="auto",
                                ),
                                dbc.Col(
                                    [
                                        html.Div("Min gain"),
                                    ],
                                    width="auto",
                                ),
                                dbc.Col(
                                    [
                                        dbc.Input(
                                            id="min_gain_input",
                                            type="number",
                                            step=0.1,
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