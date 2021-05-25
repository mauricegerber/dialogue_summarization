import sys
import pandas as pd

import dash
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go

from nltk.corpus import stopwords

sys.path.insert(0, "./lib")
import texttiling
import tfidf

def texttiling_callback(app, transcripts):
    @app.callback(
        Output(component_id="texttiling_plot", component_property="figure"),
        Output(component_id="texttiling_table", component_property="data"),
        Input(component_id="apply_texttiling_settings", component_property="n_clicks"),
        State(component_id="transcript_selector", component_property="value"),
        State(component_id="language_radio_button", component_property="value"),
        State(component_id="stopwords_input", component_property="value"),
        State(component_id="pseudosentence_length_input", component_property="value"),
        State(component_id="block_size_input", component_property="value"),
        State(component_id="n_topics_input", component_property="value"),
    )
    def apply_texttiling(n_clicks, selected_transcript, selected_language, additional_stopwords,
                        pseudosentence_length, block_size, n_topics):
        if dash.callback_context.triggered[0]["prop_id"] == "apply_texttiling_settings.n_clicks":
            transcript = transcripts[int(selected_transcript)]

            additional_stopwords_list = []
            if additional_stopwords != None:
                additional_stopwords_list = additional_stopwords.split(",")
            sw = set(stopwords.words(selected_language) + additional_stopwords_list)
            
            normalized_boundaries, boundaries, depth_scores = texttiling.texttiling(transcript, sw, pseudosentence_length,
                                                                                    block_size, n_topics)
            boundaries_timestamps = [transcript["Timestamp"][i] for i in normalized_boundaries]
            boundaries_time = [transcript["Time"][normalized_boundaries[i-1]] + " - " + transcript["Time"][normalized_boundaries[i]]
                            for i in range(1, len(normalized_boundaries))]
            
            subtopics = []
            for i in range(1, len(boundaries_timestamps)):
                transcript_subtopic = transcript[transcript["Timestamp"] < boundaries_timestamps[i]]
                transcript_subtopic = transcript_subtopic[transcript_subtopic["Timestamp"] >= boundaries_timestamps[i-1]]
                text = ""
                for utterance in transcript_subtopic["Utterance"].str.lower():
                    text += utterance
                subtopics.append(text)
                
            df = tfidf.tfidf(subtopics)
            keywords = []
            for column in df:
                keywords.append(", ".join(list(df[column].sort_values(ascending=False).index[:10])))
            
            data = {"Start time": boundaries_time, "Keywords": keywords}
            keywords_table = pd.DataFrame(data=data).to_dict("records")

            fig = go.Figure()
            fig["layout"] = go.Layout(margin={"t": 0, "b": 0, "r": 0, "l": 0})
            for i in range(len(boundaries)):
                fig.add_shape(
                    type="line",
                    x0=boundaries[i],
                    y0=0,
                    x1=boundaries[i],
                    y1=max(depth_scores),
                    line=dict(
                        color="DarkOrange",
                        width=3,
                        dash="dot",
                ))
                fig.add_annotation(
                    x=boundaries[i],
                    y=max(depth_scores)+0.03,
                    text=transcript["Time"][normalized_boundaries[i+1]],
                    showarrow=False,
                )
            fig.add_trace(go.Scatter(
                x=list(range(len(depth_scores))),
                y=depth_scores,
                mode="lines"
            ))
            fig.update_layout(
                xaxis_title="Gap between pseudosentences",
                yaxis_title="Depth score",
            )

            return fig, keywords_table

        return dash.no_update, dash.no_update