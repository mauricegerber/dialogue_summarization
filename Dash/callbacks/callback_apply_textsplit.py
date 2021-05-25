import pandas as pd

import dash
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go

# import functions
from functions.textsplit import textsplit
from functions.tfidf import tfidf

def callback_apply_textsplit(app, transcripts):
    @app.callback(
        Output(component_id="textsplit_plot", component_property="figure"),
        Output(component_id="textsplit_table", component_property="data"),
        Input(component_id="apply_textsplit_settings", component_property="n_clicks"),
        State(component_id="transcript_selector", component_property="value"),
        State(component_id="segment_length_input", component_property="value"),
    )
    def apply_textsplit(n_clicks, selected_transcript, segment_length):
        if dash.callback_context.triggered[0]["prop_id"] == "apply_textsplit_settings.n_clicks":
            transcript = transcripts[int(selected_transcript)]
            
            normalized_splits, splits, lengths_optimal = textsplit(transcript, segment_length)

            boundaries_timestamps = [transcript["Timestamp"][i] for i in normalized_splits]
            boundaries_time = [transcript["Time"][normalized_splits[i-1]] + " - " + transcript["Time"][normalized_splits[i]]
                            for i in range(1, len(normalized_splits))]
            
            subtopics = []
            for i in range(1, len(boundaries_timestamps)):
                transcript_subtopic = transcript[transcript["Timestamp"] < boundaries_timestamps[i]]
                transcript_subtopic = transcript_subtopic[transcript_subtopic["Timestamp"] >= boundaries_timestamps[i-1]]
                text = ""
                for utterance in transcript_subtopic["Utterance"].str.lower():
                    text += utterance
                subtopics.append(text)
                
            df = tfidf(subtopics)
            keywords = []
            for column in df:
                keywords.append(", ".join(list(df[column].sort_values(ascending=False).index[:10])))
            
            data = {"Start time": boundaries_time, "Keywords": keywords}
            keywords_table = pd.DataFrame(data=data).to_dict("records")

            fig = go.Figure()
            fig["layout"] = go.Layout(margin={"t": 0, "b": 0, "r": 0, "l": 0})
            # for i in range(len(boundaries)):
            #     fig.add_shape(
            #         type="line",
            #         x0=boundaries[i],
            #         y0=0,
            #         x1=boundaries[i],
            #         y1=max(depth_scores),
            #         line=dict(
            #             color="DarkOrange",
            #             width=3,
            #             dash="dot",
            #     ))
            #     fig.add_annotation(
            #         x=boundaries[i],
            #         y=max(depth_scores)+0.03,
            #         text=transcript["Time"][normalized_boundaries[i+1]],
            #         showarrow=False,
            #     )
            fig.add_trace(go.Scatter(
                x=list(range(len(lengths_optimal))),
                y=lengths_optimal,
                mode="lines"
            ))
            fig.update_layout(
                xaxis_title="Sentences",
                yaxis_title="Subtopic length",
            )

            return fig, keywords_table

        return dash.no_update, dash.no_update
