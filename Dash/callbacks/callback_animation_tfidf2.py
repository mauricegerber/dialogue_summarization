import math
import random
import pandas as pd
pd.options.mode.chained_assignment = None

import dash
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
from sklearn.preprocessing import MinMaxScaler

# import functions
from functions.tf_idf import tf_idf

def callback_animation_tfidf2(app, transcripts):
    @app.callback(
        Output(component_id="animation_tfidf2", component_property="figure"),
        Input(component_id="apply_wordcloud_settings4", component_property="n_clicks"),
        State(component_id="transcript_selector", component_property="value"),
        State(component_id="textblock_length_input4", component_property="value"),
        State(component_id="n_highest_scores_input", component_property="value"),
    )
    def animation_tfidf(n_clicks, selected_transcript, slct_min, n_highest_scores):
        if dash.callback_context.triggered[0]["prop_id"] == "apply_wordcloud_settings4.n_clicks":
            transcript = transcripts[int(selected_transcript)]
            data = transcript.to_dict("records")
            tf_dict, idf_dict, tfidf_dict, min_seq = tf_idf(data, slct_min)

            marks={i: str(min_seq[i-1])+"-"+str(min_seq[i])+" min" for i in range(1,len(min_seq))}

            for word, score in tfidf_dict.copy().items():
                if sum(score) < 0.002:
                    del tfidf_dict[word]

            number_of_words = len(tfidf_dict)

            random.x = random.sample(range(number_of_words), number_of_words)
            random.y = random.sample(range(number_of_words), number_of_words)

            grid_width = math.ceil(math.sqrt(number_of_words))
            grid_x = []
            grid_y = []

            for x in range(0,grid_width*4, 4):
                for y in range(grid_width):
                    grid_x.append(x)
                    grid_y.append(y)

            grid_x = grid_x[:number_of_words]
            grid_y = grid_y[:number_of_words]


            iteration_counter = 0
            word_col = []
            block_col = []
            gridx_col =[]
            gridy_col = []
            tfidf_col = []
            for word, score in tfidf_dict.items():
                for i in range(len(score)):
                    word_col.append(word)
                    block_col.append(i+1)
                    gridx_col.append(grid_x[iteration_counter])
                    gridy_col.append(grid_y[iteration_counter])
                    tfidf_col.append(score[i])
                iteration_counter += 1
            df = pd.DataFrame({'word': word_col, 'block': block_col, 'x': gridx_col, 'y': gridy_col, 'score': tfidf_col})

            num_blocks = range(1,len(min_seq))
            max_block = len(min_seq)-1

            scaler = MinMaxScaler(feature_range=(1, 60))
            df["marker_size"] = scaler.fit_transform(df["score"].values.reshape(-1,1))

            scaler2 = MinMaxScaler()
            df["opacity"] = scaler2.fit_transform(df["score"].values.reshape(-1,1))
            
            def Nlargestelement(l, n):
                l = list(l)
                Nlargestelement_list = []
  
                for i in range(0, n): 
                    max_value = 0
                    
                    for j in range(len(l)):     
                        if l[j] > max_value:
                            max_value = l[j]
                            
                    l.remove(max_value)
                    Nlargestelement_list.append(max_value)
                return min(Nlargestelement_list)

            blocks = df["block"].unique().tolist()

            # make figure
            fig_dict = {
                "data": [],
                "layout": {},
                "frames": []
            }

            # fill in most of layout
            fig_dict["layout"] = go.Layout(margin={'t': 0, "b":0, "r":0, "l":0}, plot_bgcolor="rgba(0,0,0,0)")
            fig_dict["layout"]["xaxis"] = {"title": "x", "showgrid": False, 'zeroline': False, 'visible': False}
            fig_dict["layout"]["yaxis"] = {"title": "y", "showgrid": False, 'zeroline': False, 'visible': False}
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
                    "prefix": "Textblock: ",
                    "visible": True,
                    "xanchor": "right"
                },
                "transition": {"duration": 400, "easing": "linear"},
                "pad": {"b": 10, "t": 50},
                "len": 0.875,
                "x": 0.1,
                "y": 0,
                "ticklen": 12,
                "steps": []
            }
            
            # make data
            block = blocks[0]
            dataset_by_block = df[df["block"] == block]

            n_word_score = Nlargestelement(dataset_by_block["score"], n_highest_scores)
            dataset_by_block.loc[dataset_by_block["score"] < n_word_score, ["marker_size"]] = 1
            dataset_by_block.loc[dataset_by_block["score"] < n_word_score, ["opacity"]] = 0

            data_dict = {
                "x": list(dataset_by_block["x"]),
                "y": list(dataset_by_block["y"]),
                "mode": "text + markers",
                "text": list(dataset_by_block["word"]),
                "textfont": dict(size = list(dataset_by_block["marker_size"])),
                "marker": {
                    "sizemode": "area",
                    "sizeref": 0.01,
                    "opacity": list(dataset_by_block["opacity"]),
                    "size": list(dataset_by_block["marker_size"]),
                },
                "customdata": dataset_by_block["score"],
                "hovertemplate": '%{text}<br>TF-IDF-Score: %{customdata:.3f}<extra></extra>'
            }
            fig_dict["data"].append(data_dict)

            for block in blocks:
                frame = {"data": [], "name": str(block)}
                dataset_by_block = df[df["block"] == block]

                n_word_score = Nlargestelement(dataset_by_block["score"], n_highest_scores)
                dataset_by_block.loc[dataset_by_block["score"] < n_word_score, ["marker_size"]] = 1
                dataset_by_block.loc[dataset_by_block["score"] < n_word_score, ["opacity"]] = 0
        
                data_dict = {
                    "x": list(dataset_by_block["x"]),
                    "y": list(dataset_by_block["y"]),
                    "mode": "text + markers",
                    "text": list(dataset_by_block["word"]),
                    "textfont": dict(size = list(dataset_by_block["marker_size"])),
                    "marker": {
                        "sizemode": "area",
                        "sizeref": 0.01,
                        "opacity": list(dataset_by_block["opacity"]),
                        "size": list(dataset_by_block["marker_size"])
                    },
                    "customdata": dataset_by_block["score"],
                    "hovertemplate": '%{text}<br>TF-IDF-Score: %{customdata:.3f}<extra></extra>'
                }
                frame["data"].append(data_dict)

                fig_dict["frames"].append(frame)
                slider_step = {"args": [
                    [block],
                    {"frame": {"duration": 0, "redraw": False},
                    "mode": "immediate",
                    "transition": {"duration": 0}}
                ],
                    "label": marks[block],
                    "method": "animate"}
                sliders_dict["steps"].append(slider_step)

            fig_dict["layout"]["sliders"] = [sliders_dict]

            fig = go.Figure(fig_dict)
            return fig
            
        return dash.no_update