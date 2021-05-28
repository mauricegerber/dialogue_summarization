import math
import pandas as pd

import dash
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go

# import functions
from functions.tf_idf import tf_idf

def callback_animation_tfidf(app, transcripts):
    @app.callback(
        Output(component_id="animation_tfidf", component_property="figure"),
        Input(component_id="apply_wordcloud_settings3", component_property="n_clicks"),
        State(component_id="transcript_selector", component_property="value"),
        State(component_id="textblock_length_input3", component_property="value"),
    )
    def animation_tfidf(n_clicks, selected_transcript, slct_min):
        if dash.callback_context.triggered[0]["prop_id"] == "apply_wordcloud_settings3.n_clicks":
            transcript = transcripts[int(selected_transcript)]
            data = transcript.to_dict("records")
            tf_dict, idf_dict, tfidf_dict, min_seq = tf_idf(data, slct_min)

            number_of_words = len(tfidf_dict)
            
            iteration_counter = 0
            word_col = []
            block_col = []
            tf_col =[]
            idf_col = []
            tfidf_col = []
            for word, counts in tfidf_dict.items():
                for i in range(len(counts)):
                    if sum(counts) > 0.001:
                        word_col.append(word)
                        block_col.append(i+1)
                        tf_col.append(tf_dict[word][i])
                        idf_col.append(idf_dict[word][0])
                        tfidf_col.append(counts[i])
                iteration_counter += 1
            df = pd.DataFrame({'word': word_col, 'block': block_col, 'x': tf_col, 'y': idf_col, 'score': tfidf_col})
            # pd.set_option("display.max_rows", None, "display.max_columns", None)
            # print(df)
            blocks = df["block"].unique().tolist()

            num_blocks = range(1,len(min_seq))
            max_block = len(min_seq)-1
            y_tickvals_range = list(num_blocks)[:-1]
            y_tickvals_range.reverse()
            
            y_tickvals = [math.log(max_block / x) for x in y_tickvals_range]
            y_ticktext = [str(x) + "/" + str(max_block) for x in y_tickvals_range]

            # make figure
            fig_dict = {
                "data": [],
                "layout": {},
                "frames": []
            }

            # fill in most of layout
            fig_dict["layout"] = go.Layout(margin={'t': 0, "b":0, "r":0, "l":0}, plot_bgcolor="rgba(0,0,0,0)")
            fig_dict["layout"]["xaxis"] = {"title": "Frequency in Block", "showgrid": True, 'zeroline': True, 'visible': True, "range": [-0.001,0.014]}
            fig_dict["layout"]["yaxis"] = {"title": "Inverse Document Frequency", "showgrid": True, 'zeroline': True, 'visible': True, "tickmode": "array", "tickvals": y_tickvals,
            "ticktext": y_ticktext, "type": "log"}
            fig_dict["layout"]["hovermode"] = "closest"
            fig_dict["layout"]["updatemenus"] = [
                {
                    "buttons": [
                        {
                            "args": [None, {"frame": {"duration": 2000, "redraw": False},
                                            "fromcurrent": True,
                                            "transition": {"duration": 1000, "easing": "linear"} # animation when clicking play
                                            }],
                            "label": "Play",
                            "method": "animate"
                        },
                        {
                            "args": [[None], {"frame": {"duration": 0, "redraw": False},
                                            "mode": "immediate",
                                            "transition": {"duration": 0}
                                            }],
                            "label": "Pause",
                            "method": "animate"
                        }
                    ],
                    "direction": "left",
                    "pad": {"r": 10, "t": 87},
                    "showactive": False,
                    "type": "buttons",
                    "x": 0.1,
                    "xanchor": "right",
                    "y": 0,
                    "yanchor": "top"
                }
            ]

            sliders_dict = {
                "active": 0,
                "yanchor": "top",
                "xanchor": "left",
                "currentvalue": {
                    "font": {"size": 20},
                    "prefix": "Text block:",
                    "visible": True,
                    "xanchor": "right"
                },
                "transition": {"duration": 400, "easing": "linear"},
                "pad": {"b": 10, "t": 50},
                "len": 0.9,
                "x": 0.1,
                "y": 0,
                "steps": []
            }

            # make data
            block = blocks[0]
            dataset_by_block = df[df["block"] == block]

            data_dict = {
                "x": list(dataset_by_block["x"]),
                "y": list(dataset_by_block["y"]),
                "mode": "text",
                "text": list(dataset_by_block["word"]),
                "marker": {
                    "sizemode": "area",
                    "sizeref": 0.01
                },
                "customdata": dataset_by_block["score"],
                "hovertemplate": '%{text}<br>TF-Score: %{x:.3f}<br>IDF-Score: %{y:.3f}<br>TF-IDF-Score: %{customdata:.3f}<extra></extra>'
            }
            fig_dict["data"].append(data_dict)

            for block in blocks:
                frame = {"data": [], "name": str(block)}
                dataset_by_block = df[df["block"] == block]

                data_dict = {
                    "x": list(dataset_by_block["x"]),
                    "y": list(dataset_by_block["y"]),
                    "mode": "text",
                    "text": list(dataset_by_block["word"]),
                    "marker": {
                        "sizemode": "area",
                        "sizeref": 0.01
                    },
                    "customdata": dataset_by_block["score"],
                    "hovertemplate": '%{text}<br>TF-Score: %{x:.3f}<br>IDF-Score: %{y:.3f}<br>TF-IDF-Score: %{customdata:.3f}<extra></extra>'
                }
                frame["data"].append(data_dict)

                fig_dict["frames"].append(frame)
                slider_step = {"args": [
                    [block],
                    {"frame": {"duration": 0, "redraw": False},
                    "mode": "immediate",
                    "transition": {"duration": 0}}
                ],
                    "label": block,
                    "method": "animate"}
                sliders_dict["steps"].append(slider_step)

            fig_dict["layout"]["sliders"] = [sliders_dict]

            fig = go.Figure(fig_dict)
            return fig
            
        return dash.no_update