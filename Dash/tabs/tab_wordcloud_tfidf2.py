import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

import plotly.graph_objects as go

def tab_wordcloud_tfidf2():
    vertical_space = "15px"
    tab = dbc.Tab(label="Wordcloud TF-IDF", children=[
        html.Div(style={"height": vertical_space}),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            children=[
                                html.Span("This tab depicts a animated graphic of the TF-IDF algorithm as a wordcloud"),
                                html.Span("With the Parameter "),
                                html.I("Textblock length "),
                                html.Span("the block length is adjusted. "),
                                html.Span("The second Parameter "),
                                html.I("n-highest score "),
                                html.Span("means that only words equal or above the n-highest TF-IDF score are depicted. As an example if it is set to 5, all the items equal and above the 5 highest score are illustrated. "),
                                html.Span("Consequently there are at least 5 words but it can also be more since words can have the same score. "),
                                html.Span("With the play button the animation runs through the different blocks and illustrates the highest TF-IDF scores of the words in this block. "),
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
                                        html.Div("Show the n-highest scores"),
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