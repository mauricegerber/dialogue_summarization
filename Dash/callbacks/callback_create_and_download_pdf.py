import os
import pandas as pd
import flask

import dash
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_bootstrap_components as dbc

# import functions
from functions.create_pdf import create_pdf

def callback_create_and_download_pdf(app):

    def build_download_button(uri):
        """Generates a download button for the resource"""
        button = html.Form(
            action=uri,
            method="get",
            target = "_blank",
            children=[
                dbc.Button(
                    id = "pdf_download_button",
                    className="btn-outline-primary",
                    disabled = False,
                    type="submit",
                    children=["download"]
                )
            ]
        )
        return button

    @app.callback(
        Output(component_id="download-area", component_property="children"),
        Output(component_id="pdf_download_button", component_property="className"),
        Output(component_id="pdf_download_button", component_property="disabled"),
        Input(component_id="pdf_generate_button", component_property="n_clicks"),
        Input(component_id="transcript_table", component_property="data")
    )
    def pdf_generate(n_clicks, current_transcript):
        trigger = dash.callback_context.triggered[0]["prop_id"]
        if trigger == "pdf_generate_button.n_clicks":
            transcript = pd.DataFrame.from_records(current_transcript)
            uri = create_pdf(transcript)
            return [build_download_button(uri)], dash.no_update, False
        return dash.no_update, "btn-secondary disabled", True

    @app.server.route('/downloadable/<path:path>')
    def serve_static(path):
        return flask.send_from_directory(
            os.path.join(".", 'downloadable'), path
        )