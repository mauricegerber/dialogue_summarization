import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

import plotly.graph_objects as go

def tab_wordcloud_tfidf():
    vertical_space = "15px"
    tab = dbc.Tab(label="TF-IDF graphic", children=[
        html.Div(style={"height": vertical_space}),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            children=[
                                html.Span("This tab depicts a animated graphic of the TF-IDF algorithm applied to the selected transcript. "),
                                html.Span("With the "),
                                html.I("Textblock length "),
                                html.Span("the block length is adjusted. "),
                                html.Span("The x-axis shows the Term Frequency score of the word in the selected block and the y-axis shows the Inverse Document Frequency score, where 1/3 means the word occurs in 1 of 3 blocks over the document. "),
                                html.Span("When the mouse is moved over the word, the total TF-IDF score can also be seen."),
                                html.Span("The higher the score, the more influencial the word in this specific block."),
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
                        dcc.Loading(
                            id="loading_wctfidf",
                            color="#1a1a1a",
                            children=[
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
    )
    return tab