import sys
import os

import pandas as pd
import statistics
from nltk.corpus import stopwords
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
pio.kaleido.scope.default_format = "png"
pio.kaleido.scope.default_width = 1920
pio.kaleido.scope.default_height = 800



# add absolute path to main directory "summarization" to system paths
sys.path.insert(0, os.path.split(os.path.split(sys.path[0])[0])[0])

from Dash.functions.calculate_timestamps import calculate_timestamps
from Dash.functions.split_dialog import split_dialog
from Dash.functions.wordcloud_pl import plot


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

data = transcript.to_dict("records")

words, min_seq, counts = split_dialog(data, 5)

dict_selected = words[5]
ldict = len(dict_selected)

# size_multiplier = 10
# for key in dict_selected.keys():
#     dict_selected[key] = dict_selected[key] * size_multiplier

# size = list(dict_selected.values())

fig = plot(dict_selected, ldict)
fig["layout"] = go.Layout(margin={'t': 0, "b":0, "r":0, "l":0},plot_bgcolor='rgba(0,0,0,0)')
fig.update_xaxes(visible=False)
fig.update_yaxes(visible=False)
#fig.update_traces(textfont_size = size)
fig.update_traces(go.Scatter(textfont=dict(color = 'darkslategray')
))

# green: '#00ad00'
fig.write_image("./images in paper/Wordcloud/wordcloud_p2.png")