import sys
import os
import math
import random

import pandas as pd
import statistics
from nltk.corpus import stopwords
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from sklearn.preprocessing import MinMaxScaler
pio.kaleido.scope.default_format = "png"
pio.kaleido.scope.default_width = 800
pio.kaleido.scope.default_height = 300



# add absolute path to main directory "summarization" to system paths
sys.path.insert(0, os.path.split(os.path.split(sys.path[0])[0])[0])

from Dash.functions.calculate_timestamps import calculate_timestamps
from Dash.functions.split_dialog import split_dialog
from Dash.functions.wordcloud_pl import plot
from Dash.functions.tf_idf import tf_idf


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

##################### WORDCLOUD TF-IDF ANIMATION ###########################
data = transcript.to_dict("records")
tf_dict, idf_dict, tfidf_dict, min_seq = tf_idf(data, 5)

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
block = blocks[6]
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
}
fig_dict["data"].append(data_dict)


frame = {"data": [], "name": str(block)}
dataset_by_block = df[df["block"] == block]


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
#fig["layout"] = go.Layout(margin={"t": 0, "b": 0, "r": 0, "l": 0})
fig.update_xaxes(range=[0.004, 0.008] )
# fig.update_yaxes(visible=False)
fig.write_image("./images in paper/Wordcloud/wordcloud_tfidf.png")
















##################### WORDCLOUD ANIMATION #############################
# pio.kaleido.scope.default_width = 800
# pio.kaleido.scope.default_height = 500
# data = transcript.to_dict("records")
# words, min_seq, word_counts = split_dialog(data, 5)

# for word, counts in word_counts.copy().items():
#     if sum(counts) <= len(min_seq):
#         del word_counts[word]

# number_of_words = len(word_counts)

# random.x = random.sample(range(number_of_words), number_of_words)
# random.y = random.sample(range(number_of_words), number_of_words)

# grid_width = math.ceil(math.sqrt(number_of_words))
# grid_x = []
# grid_y = []

# for x in range(0,grid_width*4, 4):
#     for y in range(grid_width):
#         grid_x.append(x)
#         grid_y.append(y)

# grid_x = grid_x[:number_of_words]
# grid_y = grid_y[:number_of_words]

# iteration_counter = 0

# word_col = []
# block_col = []
# count_col = []
# gridx_col =[]
# gridy_col = []
# for word, counts in word_counts.items():
#     for i in range(len(counts)):
#         word_col.append(word)
#         block_col.append(i)
#         count_col.append(counts[i])
#         gridx_col.append(grid_x[iteration_counter])
#         gridy_col.append(grid_y[iteration_counter])
#     iteration_counter += 1
# df = pd.DataFrame({'word': word_col, 'block': block_col, 'count': count_col, 'x': gridx_col, 'y': gridy_col})

# scaler = MinMaxScaler(feature_range=(1, 60))
# df["marker_size"] = scaler.fit_transform(df["count"].values.reshape(-1,1))

# scaler2 = MinMaxScaler()
# df["opacity"] = scaler2.fit_transform(df["count"].values.reshape(-1,1))

# blocks = df["block"].unique().tolist()

# block = blocks[6]
# dataset_by_block = df[df["block"] == block]

# fig_dict = {
#     "data": [],
#     "layout": {},
#     "frames": []
# }

# # fill in most of layout
# fig_dict["layout"] = go.Layout(margin={'t': 0, "b":0, "r":0, "l":0}, plot_bgcolor="rgba(0,0,0,0)")
# fig_dict["layout"]["xaxis"] = {"title": "x", "showgrid": False, 'zeroline': False, 'visible': False}
# fig_dict["layout"]["yaxis"] = {"title": "y", "showgrid": False, 'zeroline': False, 'visible': False}
# fig_dict["layout"]["hovermode"] = "closest"
# fig_dict["layout"]["updatemenus"] = [
#     {
#         "direction": "left",
#         "pad": {"r": 10, "t": 87},
#         "showactive": False,
#         "type": "buttons",
#         "x": 0.1,
#         "xanchor": "right",
#         "y": 0,
#         "yanchor": "top"
#     }
# ]

# sliders_dict = {
#     "active": 0,
#     "yanchor": "top",
#     "xanchor": "left",
#     "currentvalue": {
#         "font": {"size": 20},
#         "prefix": "Text block:",
#         "visible": True,
#         "xanchor": "right"
#     },
#     "transition": {"duration": 400, "easing": "linear"},
#     "pad": {"b": 10, "t": 50},
#     "len": 0.9,
#     "x": 0.1,
#     "y": 0,
#     "steps": []
# }

# data_dict = {
#     "x": list(dataset_by_block["x"]),
#     "y": list(dataset_by_block["y"]),
#     "mode": "text + markers",
#     "text": list(dataset_by_block["word"]),
#     "textfont": dict(size = list(dataset_by_block["marker_size"])),
#     "marker": {
#         "sizemode": "area",
#         "sizeref": 0.01,
#         "opacity": list(dataset_by_block["opacity"]),
#         "size": list(dataset_by_block["marker_size"]),
#     },
# }
# fig_dict["data"].append(data_dict)

# block = blocks[6]
# frame = {"data": [], "name": str(block)}
# dataset_by_block = df[df["block"] == block]

# data_dict = {
#     "x": list(dataset_by_block["x"]),
#     "y": list(dataset_by_block["y"]),
#     "mode": "text + markers",
#     "text": list(dataset_by_block["word"]),
#     "textfont": dict(size = list(dataset_by_block["marker_size"])),
#     "marker": {
#         "sizemode": "area",
#         "sizeref": 0.01,
#         "opacity": list(dataset_by_block["opacity"]),
#         "size": list(dataset_by_block["marker_size"])
#     },
# }
# frame["data"].append(data_dict)

# fig_dict["frames"].append(frame)
# slider_step = {"args": [
#     [block],
#     {"frame": {"duration": 0, "redraw": False},
#     "mode": "immediate",
#     "transition": {"duration": 0}}
# ],
#     "label": block,
#     "method": "animate"}
# sliders_dict["steps"].append(slider_step)

# fig_dict["layout"]["sliders"] = [sliders_dict]

# fig = go.Figure(fig_dict)
# fig["layout"] = go.Layout(margin={"t": 0, "b": 0, "r": 0, "l": 0},plot_bgcolor='rgba(0,0,0,0)')
# fig.update_xaxes(visible=False)
# fig.update_yaxes(visible=False)
# fig.write_image("./images in paper/Wordcloud/wordcloud_p3.png")




##################### WORDCLOUD DRAFT #############################
# data = transcript.to_dict("records")

# words, min_seq, counts = split_dialog(data, 5)

# dict_selected = words[6]
# ldict = len(dict_selected)

# fig = plot(dict_selected, ldict)
# fig["layout"] = go.Layout(margin={'t': 0, "b":0, "r":0, "l":0},plot_bgcolor='rgba(0,0,0,0)')
# fig.update_xaxes(visible=False)
# fig.update_yaxes(visible=False)
# #fig.update_traces(textfont_size = size)
# fig.update_traces(go.Scatter(textfont=dict(color = 'darkslategray')
# ))

# # green: '#00ad00'
# fig.write_image("./images in paper/Wordcloud/wordcloud_p2.png")