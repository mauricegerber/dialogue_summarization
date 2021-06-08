import dash_html_components as html
import dash_bootstrap_components as dbc

def tab_keywords():
    vertical_space = "15px"
    vertical_space2 = "30px"
    tab = dbc.Tab(label="Keyword extraction", children=[
        html.Div(style={"height": vertical_space}),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            children=[
                                html.Span("This tab provides implementations of four keyword extraction algorithms."),
                                html.Span(" For an explanation of the algorithms and their parameters we refer to our paper."),
                                html.Span(" When clicking"),
                                html.I(" Apply to transcript tab"),
                                html.Span(", the keywords are shown in the table in tab 1."),
                                html.Span(" Note that the execution time of KeyBERT is much longer than for the other three.")
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
                        html.H5("Language"),
                        dbc.RadioItems(
                            id="language_radio_button",
                            options=[
                                {"label": "English", "value": "english"},
                                {"label": "German", "value": "german"},
                            ],
                            value="english",
                        ),
                    ],
                    width="auto",
                ),
                dbc.Col(
                    [
                        html.H5("Keyword extractors"),
                        dbc.Checklist(
                            id="keyword_extraction_method_selector",
                            options=[
                                {"label": "TF-IDF", "value": "tf-idf"},
                                {"label": "RAKE", "value": "rake"},
                                {"label": "YAKE", "value": "yake"},
                                {"label": "KeyBERT", "value": "keybert"},
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
                            "Apply to Transcript tab",
                            id="apply_keyword_extraction_settings",
                            className="btn-outline-primary",
                        ),
                    ],
                    width="auto",
                ),
            ],
        ),
        html.Div(style={"height": vertical_space2}),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H5("TF-IDF"),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.Div("Number of"),
                                        html.Div("keywords"),
                                    ],
                                    width="auto",
                                ),
                                dbc.Col(
                                    [
                                        dbc.Input(
                                            id="tfidf_n_kws",
                                            type="number",
                                            step=1,
                                            value=3,
                                        ),
                                    ],
                                    width="auto",
                                ),
                                dbc.Col(
                                    [
                                        dbc.RadioItems(
                                            id="tfidf_radio_button",
                                            options=[
                                                {"label": "Implementation acc. to Karen Jones (1972)", "value": "karen_jones"},
                                                {"label": "Implementation acc. to sklearn library", "value": "sklearn_library"},
                                            ],
                                            value="karen_jones",
                                        ),
                                    ],
                                ),   
                            ],
                        ),
                    ],
                    width="auto",
                ),
            ],
        ),
        html.Div(style={"height": vertical_space2}),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H5("RAKE"),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.Div("Number of"),
                                        html.Div("keywords"),
                                    ],
                                    width="auto",
                                ),
                                dbc.Col(
                                    [
                                        dbc.Input(
                                            id="rake_n_kws",
                                            type="number",
                                            step=1,
                                            value=3,
                                        ),
                                    ],
                                    width="auto",
                                ),
                                dbc.Col(
                                    [
                                        html.Div("Min length of"),
                                        html.Div("keywords"),
                                    ],
                                    width="auto",
                                ),
                                dbc.Col(
                                    [
                                        dbc.Input(
                                            id="rake_min_kw_len",
                                            type="number",
                                            step=1,
                                            value=1,
                                        ),
                                    ],
                                    width="auto",
                                ),
                                dbc.Col(
                                    [
                                        html.Div("Max length of"),
                                        html.Div("keywords"),
                                    ],
                                    width="auto",
                                ),
                                dbc.Col(
                                    [
                                        dbc.Input(
                                            id="rake_max_kw_len",
                                            type="number",
                                            step=1,
                                            value=100,
                                        ),
                                    ],
                                    width="auto",
                                ),
                            ],
                        ),
                    ],
                    width="auto",
                ),
            ],
        ),
        html.Div(style={"height": vertical_space2}),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H5("YAKE"),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.Div("Number of"),
                                        html.Div("keywords"),
                                    ],
                                    width="auto",
                                ),
                                dbc.Col(
                                    [
                                        dbc.Input(
                                            id="yake_n_kws",
                                            type="number",
                                            step=1,
                                            value=3,
                                        ),
                                    ],
                                    width="auto",
                                ),
                                dbc.Col(
                                    [
                                        html.Div("Max length of"),
                                        html.Div("keywords"),
                                    ],
                                    width="auto",
                                ),
                                dbc.Col(
                                    [
                                        dbc.Input(
                                            id="yake_max_kw_len",
                                            type="number",
                                            step=1,
                                            value=3,
                                        ),
                                    ],
                                    width="auto",
                                ),
                                dbc.Col(
                                    [
                                        html.Div("Deduplication threshold"),
                                        html.Div("in the interval [0, 1]"),
                                    ],
                                    width="auto",
                                ),
                                dbc.Col(
                                    [
                                        dbc.Input(
                                            id="yake_dd_threshold",
                                            type="number",
                                            step=0.1,
                                            value=0,
                                        ),
                                    ],
                                    width="auto",
                                ),
                            ],
                        ),
                    ],
                    width="auto",
                ),
            ],
        ),
        html.Div(style={"height": vertical_space2}),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H5("KeyBERT"),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.Div("Number of"),
                                        html.Div("keywords"),
                                    ],
                                    width="auto",
                                ),
                                dbc.Col(
                                    [
                                        dbc.Input(
                                            id="keybert_n_kws",
                                            type="number",
                                            step=1,
                                            value=3,
                                        ),
                                    ],
                                    width="auto",
                                ),
                                dbc.Col(
                                    [
                                        html.Div("Min length of"),
                                        html.Div("keywords"),
                                    ],
                                    width="auto",
                                ),
                                dbc.Col(
                                    [
                                        dbc.Input(
                                            id="keybert_min_kw_len",
                                            type="number",
                                            step=1,
                                            value=1,
                                        ),
                                    ],
                                    width="auto",
                                ),
                                dbc.Col(
                                    [
                                        html.Div("Max length of"),
                                        html.Div("keywords"),
                                    ],
                                    width="auto",
                                ),
                                dbc.Col(
                                    [
                                        dbc.Input(
                                            id="keybert_max_kw_len",
                                            type="number",
                                            step=1,
                                            value=3,
                                        ),
                                    ],
                                    width="auto",
                                ),
                                dbc.Col(
                                    [
                                        html.Div("Diversity in the"),
                                        html.Div("interval [0, 1]"),
                                    ],
                                    width="auto",
                                ),
                                dbc.Col(
                                    [
                                        dbc.Input(
                                            id="keybert_diversity",
                                            type="number",
                                            step=0.1,
                                            value=0,
                                        ),
                                    ],
                                    width="auto",
                                ),
                            ],
                        ),
                    ],
                    width="auto",
                ),
            ],
        ),
    ],
    )
    return tab