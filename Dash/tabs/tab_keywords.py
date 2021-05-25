import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

def tab_keywords():
    vertical_space = "15px"
    tab = dbc.Tab(label="Keyword extraction", children=[
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
    )
    return tab