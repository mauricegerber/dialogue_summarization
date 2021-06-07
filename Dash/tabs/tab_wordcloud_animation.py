import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

import plotly.graph_objects as go

def tab_wordcloud_animation():
    vertical_space = "15px"
    tab = dbc.Tab(label="Wordcloud animation", children=[
        html.Div(style={"height": vertical_space}),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            children=[
                                html.Span("This tab illustrates an animated Wordcloud. "),
                                html.Span("With the "),
                                html.I("Textblock length "),
                                html.Span("Parameter the block length in minutes can be adjusted. "),
                                html.Span("If the play button is clicked, the animation runs through each block and depicts the most frequent used word. "),
                                html.Span("The slider can also be varried manually. The size of the circle and the text shows the frequency of the word. "),
                                html.Span("Circels are added to ensure a smooth transition. "),
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
                        dcc.Loading(
                            id="loading_wcanimation",
                            color="#1a1a1a",
                            children=[
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
    ],
    )
    return tab