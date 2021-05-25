import base64
import io
import sys

import pandas as pd

import dash
from dash.dependencies import Input, Output, State

sys.path.insert(0, "./lib")
import calculate_timestamps

def upload_and_delete_transcripts(app, transcript_files, transcripts):
    @app.callback(
        Output(component_id="transcript_selector", component_property="options"),
        Output(component_id="transcript_selector", component_property="value"),
        Output(component_id="modal", component_property="is_open"),
        Output(component_id="modal_header", component_property="children"),
        Output(component_id="modal_body", component_property="children"),
        Input(component_id="transcript_upload_button", component_property="contents"),
        Input(component_id="transcript_delete_button", component_property="n_clicks"),
        Input(component_id="modal_close_button", component_property="n_clicks"),
        State(component_id="transcript_selector", component_property="value"),
        State(component_id="transcript_upload_button", component_property="filename"),
        State(component_id="modal", component_property="is_open"),
    )
    def upload_and_delete_transcripts(list_of_contents, n_clicks_delete, n_clicks_modal,
                                      current_transcript, list_of_names, is_open):
        if is_open:
            return dash.no_update, dash.no_update, False, dash.no_update, dash.no_update

        trigger = dash.callback_context.triggered[0]["prop_id"]

        if trigger == "transcript_upload_button.contents":

            if list_of_contents is not None:
                content_type, content_string = list_of_contents.split(",")
                decoded = base64.b64decode(content_string)

                try:
                    transcript = pd.read_csv(
                        filepath_or_buffer=io.StringIO(decoded.decode("utf-8")),
                        header=0,
                        names=["Speaker", "Time", "End time", "Duration", "Utterance"],
                        usecols=["Speaker", "Time", "Utterance"]
                    )
                    calculate_timestamps.calculate_timestamps(transcript)
                    transcripts.append(transcript)
                    transcript_files.append(list_of_names)

                    return ([{"label": transcript_files[i], "value": str(i)} for i in range(len(transcript_files))],
                            str(len(transcripts)-1), False, dash.no_update, dash.no_update)

                except Exception as e:
                    return dash.no_update, dash.no_update, True, "An error occurred", str(e)

        if trigger == "transcript_delete_button.n_clicks":
            if len(transcript_files) > 1:
                transcript_files.pop(int(current_transcript))
                transcripts.pop(int(current_transcript))
                return ([{"label": transcript_files[i], "value": str(i)} for i in range(len(transcript_files))],
                        "0", False, dash.no_update, dash.no_update)
            else:
                return dash.no_update, dash.no_update, True, "An error occurred", "App must at least contain one transcript."
    
        return ([{"label": transcript_files[i], "value": str(i)} for i in range(len(transcript_files))],
                dash.no_update, False, dash.no_update, dash.no_update)