import sys
import os

import pandas as pd
import statistics
from nltk.corpus import stopwords
import plotly
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
pio.kaleido.scope.default_format = "png"
pio.kaleido.scope.default_width = 1920
pio.kaleido.scope.default_height = 500

# add absolute path to main directory "summarization" to system paths
sys.path.insert(0, os.path.split(os.path.split(sys.path[0])[0])[0])

from Dash.functions.calculate_timestamps import calculate_timestamps
from Dash.functions.texttiling import texttiling
from Dash.functions.tfidf import tfidf

transcripts_dir = "./Dash/transcripts/"
transcript_files = os.listdir(transcripts_dir)

transcripts = []
for file in transcript_files:
    transcript = pd.read_csv(
        filepath_or_buffer=transcripts_dir + file,
        header=0,
        names=["Speaker", "Time", "End time", "Duration", "Utterance"],
        usecols=["Speaker", "Time", "Utterance"]
    )
    calculate_timestamps(transcript)
    transcripts.append(transcript)

### Parameters ###
initial_transcript_index = 1
language = "english"
additional_stopwords = []
pseudosentence_length = 20
block_size = 10
n_topics = 3

transcript = transcripts[initial_transcript_index]
sw = set(stopwords.words(language) + additional_stopwords)

normalized_boundaries, boundaries, depth_scores, gap_scores = texttiling(transcript, sw, pseudosentence_length, block_size, n_topics)

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
    
df = tfidf(subtopics)
keywords = []
for column in df:
    keywords.append(", ".join(list(df[column].sort_values(ascending=False).index[:10])))

data = {"Start time": boundaries_time, "Keywords": keywords}
keywords_table = pd.DataFrame(data=data).to_dict("records")

fig = go.Figure()
fig["layout"] = go.Layout(margin={"t": 0, "b": 0, "r": 0, "l": 0})

# # plot texttiling_histogram.png
# fig.add_trace(go.Histogram(
#     x=depth_scores,
#     histnorm="probability"
# ))
# axes_title_font = dict(family="Times", size=50)
# axes_tick_font = dict(family="Times", size=40)
# space_between_axis_label_and_ticks = 40
# grid_line_width = 4
# fig.update_xaxes(
#     title="Score",
#     title_font=axes_title_font,
#     title_standoff=space_between_axis_label_and_ticks,
#     zerolinewidth=grid_line_width,
#     gridwidth=grid_line_width,
#     tickfont=axes_tick_font
# )
# fig.update_yaxes(
#     title="Probability",
#     title_font=axes_title_font,
#     title_standoff=space_between_axis_label_and_ticks,
#     zerolinewidth=grid_line_width,
#     gridwidth=grid_line_width,
#     tickfont=axes_tick_font,
#     tick0=0,
#     dtick=0.1
# )
# fig.write_image("./Images in paper/TextTiling/texttiling_histogram.png")

# # plot texttiling_cutoff.png
# fig.add_trace(go.Scatter(
#     x=list(range(len(depth_scores))),
#     y=depth_scores,
#     mode="lines",
#     line=dict(width=4),
#     showlegend = False
# ))
# fig.add_trace(go.Scatter(
#     x=[0],
#     y=[0],
#     mode="lines",
#     line=dict(
#         width=4,
#     ),
#     name = "Mean"
# ))
# fig.add_trace(go.Scatter(
#     x=[0],
#     y=[0],
#     mode="lines",
#     line=dict(
#         width=4,
#     ),
#     name = "LC"
# ))
# fig.add_trace(go.Scatter(
#     x=[0],
#     y=[0],
#     mode="lines",
#     line=dict(
#         width=4,
#     ),
#     name = "HC"
# ))
# fig.add_shape(
#     type="line",
#     x0=0,
#     y0=statistics.mean(depth_scores),
#     x1=len(depth_scores),
#     y1=statistics.mean(depth_scores),
#     line=dict(
#         width=4,
#         color="#ff7f0e"
#     )
# )
# fig.add_shape(
#     type="line",
#     x0=0,
#     y0=statistics.mean(depth_scores) - statistics.stdev(depth_scores),
#     x1=len(depth_scores),
#     y1=statistics.mean(depth_scores) - statistics.stdev(depth_scores),
#     line=dict(
#         width=4,
#         color="#2ca02c",
#     )
# )
# fig.add_shape(
#     type="line",
#     x0=0,
#     y0=statistics.mean(depth_scores) - statistics.stdev(depth_scores)/2,
#     x1=len(depth_scores),
#     y1=statistics.mean(depth_scores) - statistics.stdev(depth_scores)/2,
#     line=dict(
#         width=4,
#         color="#9467bd",
#     )
# )
# axes_title_font = dict(family="Times", size=50)
# axes_tick_font = dict(family="Times", size=40)
# space_between_axis_label_and_ticks = 40
# grid_line_width = 4
# fig.update_layout(
#     legend=dict(
#         yanchor="top",
#         xanchor="right",
#         x=1
#     ),
#     font=axes_tick_font
# )
# fig.update_xaxes(
#     title="Gap",
#     title_font=axes_title_font,
#     title_standoff=space_between_axis_label_and_ticks,
#     zerolinewidth=grid_line_width,
#     gridwidth=grid_line_width,
#     tickfont=axes_tick_font
# )
# fig.update_yaxes(
#     title="Score",
#     title_font=axes_title_font,
#     title_standoff=space_between_axis_label_and_ticks,
#     zerolinewidth=grid_line_width,
#     gridwidth=grid_line_width,
#     tickfont=axes_tick_font,
#     tick0=0,
#     dtick=0.1
# )
# fig.write_image("./Images in paper/TextTiling/texttiling_cutoff.png")

# # plot texttiling_kX.png
# parameters = [5, 10, 20]
# for parameter in parameters:
#     fig = go.Figure()
#     fig["layout"] = go.Layout(margin={"t": 0, "b": 0, "r": 0, "l": 0})
#     normalized_boundaries, boundaries, depth_scores, gap_scores = texttiling(transcript, sw, pseudosentence_length, parameter, n_topics)
#     fig.add_trace(go.Scatter(
#         x=list(range(len(depth_scores))),
#         y=depth_scores,
#         mode="lines",
#         line=dict(width=4)
#     ))
#     axes_title_font = dict(family="Times", size=50)
#     axes_tick_font = dict(family="Times", size=40)
#     space_between_axis_label_and_ticks = 40
#     grid_line_width = 4
#     fig.add_annotation(
#         xref="paper",
#         yref="paper",
#         x=1,
#         y=1,
#         text="Block size k = " + str(parameter),
#         font=axes_tick_font,
#         bgcolor="#FFFFFF",
#         showarrow=False,
#     )
#     fig.update_xaxes(
#         title="Gap",
#         title_font=axes_title_font,
#         title_standoff=space_between_axis_label_and_ticks,
#         zerolinewidth=grid_line_width,
#         gridwidth=grid_line_width,
#         tickfont=axes_tick_font
#     )
#     fig.update_yaxes(
#         title="Score",
#         title_font=axes_title_font,
#         title_standoff=space_between_axis_label_and_ticks,
#         zerolinewidth=grid_line_width,
#         gridwidth=grid_line_width,
#         tickfont=axes_tick_font,
#         tick0=0,
#         dtick=0.1,
#         range=[0, 0.6]
#     )
#     fig.write_image("./Algorithms/texttiling_k" + str(parameter) + ".png")

# # plot texttiling_wX.png
# parameters = [10, 20, 30]
# for parameter in parameters:
#     fig = go.Figure()
#     fig["layout"] = go.Layout(margin={"t": 0, "b": 0, "r": 0, "l": 0})
#     normalized_boundaries, boundaries, depth_scores, gap_scores = texttiling(transcript, sw, parameter, block_size, n_topics)
#     fig.add_trace(go.Scatter(
#         x=list(range(len(depth_scores))),
#         y=depth_scores,
#         mode="lines",
#         line=dict(width=4)
#     ))
#     axes_title_font = dict(family="Times", size=50)
#     axes_tick_font = dict(family="Times", size=40)
#     space_between_axis_label_and_ticks = 40
#     grid_line_width = 4
#     fig.add_annotation(
#         xref="paper",
#         yref="paper",
#         x=1,
#         y=1,
#         text="Pseudosentence length w = " + str(parameter),
#         font=axes_tick_font,
#         bgcolor="#FFFFFF",
#         showarrow=False,
#     )
#     fig.update_xaxes(
#         title="Gap",
#         title_font=axes_title_font,
#         title_standoff=space_between_axis_label_and_ticks,
#         zerolinewidth=grid_line_width,
#         gridwidth=grid_line_width,
#         tickfont=axes_tick_font
#     )
#     fig.update_yaxes(
#         title="Score",
#         title_font=axes_title_font,
#         title_standoff=space_between_axis_label_and_ticks,
#         zerolinewidth=grid_line_width,
#         gridwidth=grid_line_width,
#         tickfont=axes_tick_font,
#         tick0=0,
#         dtick=0.1,
#         range=[0, 0.6]
#     )
#     fig.write_image("./Algorithms/texttiling_w" + str(parameter) + ".png")

# # plot texttiling_gap_and_depth_score.png
# fig.add_trace(go.Scatter(
#     x=list(range(len(depth_scores))),
#     y=depth_scores,
#     mode="lines",
#     line=dict(width=4),
#     name="Depth score"
# ))
# fig.add_trace(go.Scatter(
#     x=list(range(len(gap_scores))),
#     y=gap_scores,
#     mode="lines",
#     line=dict(width=4),
#     name="Gap score"
# ))
# axes_title_font = dict(family="Times", size=50)
# axes_tick_font = dict(family="Times", size=40)
# space_between_axis_label_and_ticks = 40
# grid_line_width = 4
# fig.update_layout(
#     legend=dict(
#         yanchor="top",
#         xanchor="right",
#         x=1
#     ),
#     font=axes_tick_font
# )
# fig.update_xaxes(
#     title="Gap",
#     title_font=axes_title_font,
#     title_standoff=space_between_axis_label_and_ticks,
#     zerolinewidth=grid_line_width,
#     gridwidth=grid_line_width,
#     tickfont=axes_tick_font
# )
# fig.update_yaxes(
#     title="Score",
#     title_font=axes_title_font,
#     title_standoff=space_between_axis_label_and_ticks,
#     zerolinewidth=grid_line_width,
#     gridwidth=grid_line_width,
#     tickfont=axes_tick_font,
#     tick0=0,
#     dtick=0.1
# )
# fig.write_image("./Algorithms/texttiling_gap_and_depth_score.png")

# # plot texttiling_depth_score.png
# fig.add_trace(go.Scatter(
#     x=list(range(len(depth_scores))),
#     y=depth_scores,
#     mode="lines",
#     line=dict(width=4)
# ))
# axes_title_font = dict(family="Times", size=50)
# axes_tick_font = dict(family="Times", size=40)
# space_between_axis_label_and_ticks = 40
# grid_line_width = 4
# fig.update_xaxes(
#     title="Gap",
#     title_font=axes_title_font,
#     title_standoff=space_between_axis_label_and_ticks,
#     zerolinewidth=grid_line_width,
#     gridwidth=grid_line_width,
#     tickfont=axes_tick_font
# )
# fig.update_yaxes(
#     title="Score",
#     title_font=axes_title_font,
#     title_standoff=space_between_axis_label_and_ticks,
#     zerolinewidth=grid_line_width,
#     gridwidth=grid_line_width,
#     tickfont=axes_tick_font,
#     tick0=0,
#     dtick=0.1
# )
# fig.write_image("./Algorithms/texttiling_depth_score.png")

# # plot texttiling_gap_score.png
# fig.add_trace(go.Scatter(
#     x=list(range(len(gap_scores))),
#     y=gap_scores,
#     mode="lines",
#     line=dict(width=4)
# ))
# axes_title_font = dict(family="Times", size=50)
# axes_tick_font = dict(family="Times", size=40)
# space_between_axis_label_and_ticks = 40
# grid_line_width = 4
# fig.update_xaxes(
#     title="Gap",
#     title_font=axes_title_font,
#     title_standoff=space_between_axis_label_and_ticks,
#     zerolinewidth=grid_line_width,
#     gridwidth=grid_line_width,
#     tickfont=axes_tick_font
# )
# fig.update_yaxes(
#     title="Score",
#     title_font=axes_title_font,
#     title_standoff=space_between_axis_label_and_ticks,
#     zerolinewidth=grid_line_width,
#     gridwidth=grid_line_width,
#     tickfont=axes_tick_font,
#     tick0=0,
#     dtick=0.1
# )
# fig.write_image("./Algorithms/texttiling_gap_score.png")