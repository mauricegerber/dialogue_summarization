import sys
import os

from nltk.tokenize import word_tokenize
import word2vec
import pandas as pd
import numpy as np
from numpy.linalg import norm
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import CountVectorizer

import plotly
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
pio.kaleido.scope.default_format = "png"
pio.kaleido.scope.default_width = 1920
pio.kaleido.scope.default_height = 500

sys.path.insert(0, os.path.split(sys.path[0])[0])
path = sys.path[0]

sentences = [
    "this is the first sentence of the document",
    "in this text this is the second phrase",
    "is this the fourth sentence",
    "the sky is blue and trees are green",
    "water is blue too but trees can also be red"
]
word_selection = ["sentence", "document", "text", "phrase", "sky", "trees", "water"]
unique_words = list(set(word_tokenize(" ".join(sentences))))

wrdvec_path = path + "/Dash/functions/wrdvecs.bin"
model = word2vec.load(wrdvec_path)
wrdvecs = pd.DataFrame(model.vectors, index=model.vocab) # [71291 rows x 3 columns]

wrdvecs_array = wrdvecs.to_numpy()
pca = PCA(n_components=3, random_state=1234)
wrdvecs_array_reduced = pca.fit_transform(wrdvecs_array)
wrdvecs_reduced = pd.DataFrame(wrdvecs_array_reduced, index=model.vocab) # [71291 rows x 3 columns]
del model

vecr = CountVectorizer(vocabulary=wrdvecs_reduced.index)
sentence_vectors = vecr.transform(sentences).dot(wrdvecs_reduced) # (5, 3)
# print(sentence_vectors)

docmat = sentence_vectors
L, dim = docmat.shape # (5, 3)
print(docmat)

cumvecs = np.cumsum(np.vstack((np.zeros((1, dim)), docmat)), axis=0)

print(cumvecs)
print("---")

cuts = [0, L]
segscore = dict()
# ord=2 is Euclidean norm
# distance from S5 to origin
segscore[0] = norm(cumvecs[L, :] - cumvecs[0, :], ord=2) # 3.2873382563619793
segscore[L] = 0 # corner case, always 0
# distance from origin, S1, S2, S3, S4 to origin
score_l = norm(cumvecs[:L, :] - cumvecs[0, :], axis=1, ord=2) # [0.         0.99858612 1.80674872 2.35113845 2.34269185]
# distance from S5 to origin, S1, S2, S3, S4
score_r = norm(cumvecs[L, :] - cumvecs[:L, :], axis=1, ord=2) # [3.28733826 2.62140743 2.07435777 1.87815312 1.40863458]

score_out = np.zeros(L)
score_out[0] = -np.inf # forbidden split position
score = score_out + score_l + score_r # [      -inf 3.61999355 3.88110648 4.22929158 3.75132643]

# origin - origin + S5 - origin --> no split allowed
# S1 - origin     + S5 - S1
# S2 - origin     + S5 - S2
# S3 - origin     + S5 - S3 --> max
# S4 - origin     + S5 - S4

max_splits = 1
min_gain = np.inf
counter = 0
while True:
    counter += 1
    print("Iteration count: ", counter)
    split = np.argmax(score) # index of highest score
    print("Split: ", split)

    if score[split] == - np.inf:
        break

    cut_l = max([c for c in cuts if c < split]) # max of all c's to the left of the current highest score
    print("cut_l: ", cut_l)
    cut_r = min([c for c in cuts if split < c]) # min of all c's to the right of the current highest score
    print("cut_r: ", cut_r)
    # first iteration: S3 - origin + S5 - S3 is 0.94 longer than S5 - origin
    split_gain = score_l[split] + score_r[split] - segscore[cut_l]
    print("split_gain: ", split_gain)

    min_gain = min(min_gain, split_gain) # smallest gain across all while loop iterations

    # first iteration: segscore at 0 is set to distance from S3 to origin
    segscore[cut_l] = score_l[split]
    # first iteration: segscore at 3 is set to distance from S5 to S3
    segscore[split] = score_r[split]
    print("segscore: ", segscore)

    cuts.append(split)
    cuts = sorted(cuts)
    print("cuts: ", cuts)

    if max_splits is not None:
        if len(cuts) >= max_splits + 2:
            break

    # original: distance from origin, S1, S2, S3, S4 to origin
    # first iteration: distance from S3, S4 to S3
    score_l[split:cut_r] = norm(cumvecs[split:cut_r, :] - cumvecs[split, :], axis=1, ord=2)
    # [0.         0.99858612 1.80674872 2.35113845 2.34269185] initial score_l
    # [0.         0.99858612 1.80674872 0.         0.50518443] score_l after first iteration

    # original: # distance from S5 to origin, S1, S2, S3, S4
    # first iteration: distance from S3 to origin, S1, S2
    score_r[cut_l:split] = norm(cumvecs[split, :] - cumvecs[cut_l:split, :], axis=1, ord=2)
    # [3.28733826 2.62140743 2.07435777 1.87815312 1.40863458] initial score_r
    # [2.35113845 1.36641848 0.54490199 1.87815312 1.40863458] score_r after first iteration

    score_out[cut_l:split] += segscore[split] - split_gain
    score_out[split:cut_r] += segscore[cut_l] - split_gain
    score_out[split] = -np.inf

    print("score_out: ", score_out)

    # update score
    score = score_out + score_l + score_r

    # origin - origin + S3 - origin + -inf --> no split allowed
    # S1 - origin     + S3 - S1     + score of segment minus split_gain
    # S2 - origin     + S3 - S2     + score of segment minus split_gain
    # S3 - S3         + S5 - S3     + -inf --> no split allowed
    # S4 - S3         + S5 - S4     + score of segment minus split_gain

    print("score: ", score)
    print("---")

# coord_texts = ["0", "1", "2", "3", "4", "5"]
# fig = go.Figure()
# fig.add_trace(go.Scatter3d(
#     x=cumvecs[:,0],
#     y=cumvecs[:,1],
#     z=cumvecs[:,2],
#     text=coord_texts,
#     textfont=dict(
#         family="Times",
#         size=20,
#     ),
#     mode="text",
# ))
# for row in cumvecs[:3, :]:
#     fig.add_trace(go.Scatter3d(
#         x=[0, row[0]],
#         y=[0, row[1]],
#         z=[0, row[2]],
#         mode="lines",
#         line=dict(
#             color="red",
#             width=4,
#         ),
#     ))
# fig.add_trace(go.Scatter3d(
#     x=[cumvecs[3,0], cumvecs[4,0]],
#     y=[cumvecs[3,1], cumvecs[4,1]],
#     z=[cumvecs[3,2], cumvecs[4,2]],
#     mode="lines",
#     line=dict(
#         color="red",
#         width=4,
#     ),
# ))
# for row in cumvecs[3:, :]:
#     fig.add_trace(go.Scatter3d(
#         x=[cumvecs[-1,0], row[0]],
#         y=[cumvecs[-1,1], row[1]],
#         z=[cumvecs[-1,2], row[2]],
#         mode="lines",
#         line=dict(
#             color="green",
#             width=4,
#         ),
#     ))
# for row in cumvecs[:3, :]:
#     fig.add_trace(go.Scatter3d(
#         x=[cumvecs[3,0], row[0]],
#         y=[cumvecs[3,1], row[1]],
#         z=[cumvecs[3,2], row[2]],
#         mode="lines",
#         line=dict(
#             color="green",
#             width=4,
#         ),
#     ))
# axes_title_font = dict(family="Times", size=40)
# axes_tick_font = dict(family="Times", size=15)
# fig.update_layout(scene = dict(
#     xaxis = dict(
#         range=[-2, 1],
#         dtick=0.5,
#         title_font=axes_title_font,
#         tickfont=axes_tick_font,
#         backgroundcolor="rgb(200, 200, 230)",
#         gridcolor="white",
#         showbackground=True,
#         zerolinecolor="white",),
#     yaxis = dict(
#         range=[-3, 1],
#         dtick=0.5,
#         title_font=axes_title_font,
#         tickfont=axes_tick_font,
#         backgroundcolor="rgb(230, 200,230)",
#         gridcolor="white",
#         showbackground=True,
#         zerolinecolor="white"),
#     zaxis = dict(
#         range=[-0.5, 2.5],
#         dtick=0.5,
#         title_font=axes_title_font,
#         tickfont=axes_tick_font,
#         backgroundcolor="rgb(230, 230,200)",
#         gridcolor="white",
#         showbackground=True,
#         zerolinecolor="white",),),
# )
# fig.show()

# coord_texts = ["0", "1", "2", "3", "4", "5"]
# fig = go.Figure()
# fig.add_trace(go.Scatter3d(
#     x=cumvecs[:,0],
#     y=cumvecs[:,1],
#     z=cumvecs[:,2],
#     text=coord_texts,
#     textfont=dict(
#         family="Times",
#         size=20,
#     ),
#     mode="text",
# ))
# for row in cumvecs[:L, :]:
#     fig.add_trace(go.Scatter3d(
#         x=[0, row[0]],
#         y=[0, row[1]],
#         z=[0, row[2]],
#         mode="lines",
#         line=dict(
#             color="red",
#             width=4,
#         ),
#     ))
# for row in cumvecs[:L, :]:
#     fig.add_trace(go.Scatter3d(
#         x=[cumvecs[-1,0], row[0]],
#         y=[cumvecs[-1,1], row[1]],
#         z=[cumvecs[-1,2], row[2]],
#         mode="lines",
#         line=dict(
#             color="green",
#             width=4,
#         ),
#     ))
# axes_title_font = dict(family="Times", size=40)
# axes_tick_font = dict(family="Times", size=15)
# fig.update_layout(scene = dict(
#     xaxis = dict(
#         range=[-2, 1],
#         dtick=0.5,
#         title_font=axes_title_font,
#         tickfont=axes_tick_font,
#         backgroundcolor="rgb(200, 200, 230)",
#         gridcolor="white",
#         showbackground=True,
#         zerolinecolor="white",),
#     yaxis = dict(
#         range=[-3, 1],
#         dtick=0.5,
#         title_font=axes_title_font,
#         tickfont=axes_tick_font,
#         backgroundcolor="rgb(230, 200,230)",
#         gridcolor="white",
#         showbackground=True,
#         zerolinecolor="white"),
#     zaxis = dict(
#         range=[-0.5, 2.5],
#         dtick=0.5,
#         title_font=axes_title_font,
#         tickfont=axes_tick_font,
#         backgroundcolor="rgb(230, 230,200)",
#         gridcolor="white",
#         showbackground=True,
#         zerolinecolor="white",),),
# )
# fig.show()

# coord_texts = ["0", "1", "2", "3", "4", "5"]
# fig = go.Figure()
# fig.add_trace(go.Scatter3d(
#     x=cumvecs[:,0],
#     y=cumvecs[:,1],
#     z=cumvecs[:,2],
#     text=coord_texts,
#     textfont=dict(
#         family="Times",
#         size=20,
#     ),
#     mode="text",
# ))
# axes_title_font = dict(family="Times", size=40)
# axes_tick_font = dict(family="Times", size=15)
# fig.update_layout(scene = dict(
#     xaxis = dict(
#         range=[-2, 1],
#         dtick=0.5,
#         title_font=axes_title_font,
#         tickfont=axes_tick_font,
#         backgroundcolor="rgb(200, 200, 230)",
#         gridcolor="white",
#         showbackground=True,
#         zerolinecolor="white",),
#     yaxis = dict(
#         range=[-3, 1],
#         dtick=0.5,
#         title_font=axes_title_font,
#         tickfont=axes_tick_font,
#         backgroundcolor="rgb(230, 200,230)",
#         gridcolor="white",
#         showbackground=True,
#         zerolinecolor="white"),
#     zaxis = dict(
#         range=[-0.5, 2.5],
#         dtick=0.5,
#         title_font=axes_title_font,
#         tickfont=axes_tick_font,
#         backgroundcolor="rgb(230, 230,200)",
#         gridcolor="white",
#         showbackground=True,
#         zerolinecolor="white",),),
# )
# fig.show()

# coord_texts = ["Sent. 1", "Sent. 2", "Sent. 3", "Sent. 4", "Sent. 5"]
# fig = go.Figure()
# fig.add_trace(go.Scatter3d(
#     x=sentence_vectors[:,0],
#     y=sentence_vectors[:,1],
#     z=sentence_vectors[:,2],
#     text=coord_texts,
#     textfont=dict(
#         family="Times",
#         size=20,
#     ),
#     mode="text",
# ))
# axes_title_font = dict(family="Times", size=40)
# axes_tick_font = dict(family="Times", size=15)
# fig.update_layout(scene = dict(
#     xaxis = dict(
#         range=[-2, 1],
#         dtick=0.5,
#         title_font=axes_title_font,
#         tickfont=axes_tick_font,
#         backgroundcolor="rgb(200, 200, 230)",
#         gridcolor="white",
#         showbackground=True,
#         zerolinecolor="white",),
#     yaxis = dict(
#         range=[-2, 1],
#         dtick=0.5,
#         title_font=axes_title_font,
#         tickfont=axes_tick_font,
#         backgroundcolor="rgb(230, 200,230)",
#         gridcolor="white",
#         showbackground=True,
#         zerolinecolor="white"),
#     zaxis = dict(
#         range=[-0.5, 1.5],
#         dtick=0.5,
#         title_font=axes_title_font,
#         tickfont=axes_tick_font,
#         backgroundcolor="rgb(230, 230,200)",
#         gridcolor="white",
#         showbackground=True,
#         zerolinecolor="white",),),
# )
# fig.show()

# wrdvecs_array_reduced_even_more = wrdvecs_reduced[wrdvecs_reduced.index.isin(word_selection)]
# fig = go.Figure()
# fig.add_trace(go.Scatter3d(
#     x=wrdvecs_array_reduced_even_more[2],
#     y=wrdvecs_array_reduced_even_more[1],
#     z=wrdvecs_array_reduced_even_more[0],
#     text=wrdvecs_array_reduced_even_more.index,
#     textfont=dict(
#         family="Times",
#         size=20,
#     ),
#     mode="text",
# ))
# axes_title_font = dict(family="Times", size=40)
# axes_tick_font = dict(family="Times", size=15)
# fig.update_layout(scene = dict(
#     xaxis = dict(
#         range=[-0.3, 0.2],
#         title_font=axes_title_font,
#         tickfont=axes_tick_font,
#         backgroundcolor="rgb(200, 200, 230)",
#         gridcolor="white",
#         showbackground=True,
#         zerolinecolor="white",),
#     yaxis = dict(
#         range=[-0.2, 0.1],
#         title_font=axes_title_font,
#         tickfont=axes_tick_font,
#         backgroundcolor="rgb(230, 200,230)",
#         gridcolor="white",
#         showbackground=True,
#         zerolinecolor="white"),
#     zaxis = dict(
#         range=[-0.1, 0.1],
#         title_font=axes_title_font,
#         tickfont=axes_tick_font,
#         backgroundcolor="rgb(230, 230,200)",
#         gridcolor="white",
#         showbackground=True,
#         zerolinecolor="white",),),
# )
# fig.show()