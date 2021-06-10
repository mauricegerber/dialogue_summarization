import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

import plotly.graph_objects as go

def tab_wordcloud_tfidf2():
    vertical_space = "15px"
    tab = dbc.Tab(label="Wordcloud animation TF-IDF", children=[
        html.Div(style={"height": vertical_space}),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            children=[
                                html.Span("This tab provides an animated Wordcloud using TF-IDF."),
                                html.Span(" With the first parameter "),
                                html.I("Textblock length"),
                                html.Span(" the block length in minutes can be adjusted."),
                                html.Span(" With the second parameter "),
                                html.I("n highest scores"),
                                html.Span(" the number of words displayed can be reduced."),
                                html.Span(" When clicking the play button, the animation runs through each textblock and depicts the words with the highest TF-IDF scores in the current block."),
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
                                        html.Div("Textblock length"),
                                        html.Div("in minutes"),
                                    ],
                                    width="auto",
                                ),
                                dbc.Col(
                                    [
                                        dbc.Input(
                                            id="textblock_length_input4",
                                            type="number",
                                            min=1,
                                            max=100,
                                            step=1,
                                            value=5,
                                        ),
                                    ],
                                    width="auto",
                                ),

                                dbc.Col(
                                    [
                                        html.Div("Show n-highest scores"),
                                    ],
                                    width="auto",
                                ),
                                dbc.Col(
                                    [
                                        dbc.Input(
                                            id="n_highest_scores_input",
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
                            id="apply_wordcloud_settings4",
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
                        dcc.Loading(
                            id="loading_wctfidf2",
                            color="#1a1a1a",
                            children=[
                                dcc.Graph(
                                    id="animation_tfidf2",
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
    )
    return tab