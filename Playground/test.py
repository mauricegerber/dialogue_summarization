import sys
import os
import word2vec
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer
import random

import numpy as np
from numpy.linalg import norm

from collections import namedtuple

def get_penalty(docmats, segment_len):
    """
    Determine penalty for segments having length `segment_len` on average.
    This is achieved by stochastically rounding the expected number
    of splits per document `max_splits` and taking the minimal split_gain that
    occurs in split_greedy given `max_splits`.
    """
    penalties = []
    # there is only one iteration through this for loop as there is only one matrix
    for docmat in docmats:
        avg_n_seg = docmat.shape[0] / segment_len # docmat.shape[0] = number of rows in the matrix (number of sentences)
        max_splits = int(avg_n_seg) + (random.random() < avg_n_seg % 1) - 1 # random.random() = runif [0, 1]
        if max_splits >= 1:
            seg = split_greedy(docmat, max_splits=max_splits)
            print(seg)
            if seg.min_gain < np.inf:
                penalties.append(seg.min_gain)
    if len(penalties) > 0:
        return np.mean(penalties)
    raise ValueError('All documents too short for given segment_len.')

Segmentation = namedtuple('Segmentation',
                          'total splits gains min_gain optimal')

def split_greedy(docmat, penalty=None, max_splits=None):
    """
    Iteratively segment a document into segments being greedy about the
    next choice. This gives very accurate results on crafted documents, i.e.
    artificial concatenations of random documents.
    `penalty` is the minimum quantity a split has to improve the score to be
    made. If not given `total` is not computed.
    `max_splits` is a limit on the number of splits.
    Either `penalty` or `max_splits` have to be given.
    Whenever the iteration reaches the while block the following holds:
    `cuts` == splits + [L] where splits are the segment start indices
    `segscore` maps all segment start indices to segment vector lengths
    `score_l[i]` is the cumulated vector length from the cut left of i to i
    `score_r[i]` is the cumulated vector length from i to the cut right of i
    `score_out[i]` is the sum of all segscores not including the segment at i
    `scores[i]` is the sum of all segment vector lengths if we split at i
    These quantities are repaired after determining a next split from `scores`.
    Returns `total`, `splits`, `gains` where
    - `total` is the score diminished by len(splits) * penalty to make it
      continuous in the input. It is comparable to the output of split_optimal.
    - `splits` is the list of splits
    - `gains` is a list of uplift each split contributes vs. leaving it out
    Note: The splitting strategy suggests all resulting splits will have gain at
    least `penalty`. This is not the case as new splits can decrease the gain
    of others. This can be repaired by blocking positions where a split would
    decrease the gain of an existing one to less than `penalty` but is not
    implemented here.
    """
    L, dim = docmat.shape # number of rows (sentences), number of columns (dimensions of vector space)

    assert max_splits is not None or (penalty is not None and penalty > 0)

    # norm(cumvecs[j] - cumvecs[i]) == norm(w_i + ... + w_{j-1})
    cumvecs = np.cumsum(np.vstack((np.zeros((1, dim)), docmat)), axis=0)
    # np.zeros((1, dim)) = row vector 1 x dim
    # np.vstack((np.zeros((1, dim)), docmat)) = stack row vector np.zeros on top of docmat increasing its row count by 1
    # np.cumsum(np.vstack((np.zeros((1, dim)), docmat)), axis=0) = cumulative sum over rows

    # cut[0] seg[0] cut[1] seg[1] ... seg[L-1] cut[L]
    cuts = [0, L]
    segscore = dict()
    # ord=2 is Euclidean norm
    segscore[0] = norm(cumvecs[L, :] - cumvecs[0, :], ord=2) # last row - first row
    segscore[L] = 0 # corner case, always 0
    # all rows except last - first row, norm of each row except last is calculated (vector lengths are calculated across dim)
    score_l = norm(cumvecs[:L, :] - cumvecs[0, :], axis=1, ord=2)
    # last row - all rows except last, norm of each row except last is calculated (vector lengths are calculated across dim)
    score_r = norm(cumvecs[L, :] - cumvecs[:L, :], axis=1, ord=2)
    score_out = np.zeros(L)
    score_out[0] = -np.inf # forbidden split position
    score = score_out + score_l + score_r # length equals number of rows (sentences)

    counter = 0

    #print(score_l)
    #print(score_r)

    min_gain = np.inf
    while True:
        counter += 1
        #print("iteration count: ", counter)
        split = np.argmax(score) # index of highest score
        #print("split: ", split)

        if score[split] == - np.inf:
            break

        cut_l = max([c for c in cuts if c < split]) # max of all c's to the left of the current highest score
        #print(cut_l)
        cut_r = min([c for c in cuts if split < c]) # min of all c's to the right of the current highest score
        #print(cut_r)
        split_gain = score_l[split] + score_r[split] - segscore[cut_l]
        #print(split_gain)
        if penalty is not None:
            if split_gain < penalty:
                break

        min_gain = min(min_gain, split_gain) # smallest gain across all while loop iterations

        segscore[cut_l] = score_l[split]
        segscore[split] = score_r[split]
        #print("segscore: ", segscore)

        cuts.append(split)
        cuts = sorted(cuts)
        #print("cuts: ", cuts)

        if max_splits is not None:
            if len(cuts) >= max_splits + 2:
                break

        # differential changes to score arrays
        # subtract current split row from all rows to the right of the current split
        score_l[split:cut_r] = norm(cumvecs[split:cut_r, :] - cumvecs[split, :], axis=1, ord=2)
        # subtract all rows to the left of the current split from the current split row
        score_r[cut_l:split] = norm(cumvecs[split, :] - cumvecs[cut_l:split, :], axis=1, ord=2)

        #print(score_l)
        #print(score_r)

        # adding following constant not necessary, only for score semantics
        score_out += split_gain
        score_out[cut_l:split] += segscore[split] - split_gain
        score_out[split:cut_r] += segscore[cut_l] - split_gain
        score_out[split] = -np.inf

        # update score
        score = score_out + score_l + score_r

    cuts = sorted(cuts)
    splits = cuts[1:-1]
    if penalty is None:
        total = None
    else:
        total = sum(
            norm(cumvecs[l, :] - cumvecs[r, :], ord=2)
            for l, r in zip(cuts[: -1], cuts[1:])) - len(splits) * penalty
    gains = []
    for beg, cen, end in zip(cuts[:-2], cuts[1:-1], cuts[2:]):
        no_split_score = norm(cumvecs[end, :] - cumvecs[beg, :], ord=2)
        gains.append(segscore[beg] + segscore[cen] - no_split_score)

    return Segmentation(total, splits, gains,
                        min_gain=min_gain, optimal=None)

###############################################################################################################################
# add absolute path to main directory "summarization" to system paths
sys.path.insert(0, os.path.split(sys.path[0])[0])
path = sys.path[0]
# Vice presidential debate.csv
# Job interview.csv

transcript = pd.read_csv(
    filepath_or_buffer=path + "/Dash/transcripts/Job interview.csv",
    header=0,
    names=["Speaker", "Time", "End time", "Duration", "Utterance"],
    usecols=["Speaker", "Time", "Utterance"]
)
text = ""
for utterance in transcript["Utterance"].str.lower():
    text += utterance + " "

wrdvec_path = path + '/Dash/functions/wrdvecs.bin'
model = word2vec.load(wrdvec_path)
wrdvecs = pd.DataFrame(model.vectors, index=model.vocab) # dataframe with [71291 rows x 200 columns], row indices are words
del model
print(wrdvecs.shape)

from textsplit.tools import SimpleSentenceTokenizer
sentence_tokenizer = SimpleSentenceTokenizer()

from textsplit.tools import get_segments
from textsplit.algorithm import split_optimal, get_total

segment_len = 60  # segment target length in sentences

sentenced_text = sentence_tokenizer(text) # list of sentences (137 sentences)
print(len(sentenced_text))


vecr = CountVectorizer(vocabulary=wrdvecs.index) # the vocabulary are all words from the word2vec model (71291 words)
sentence_vectors = vecr.transform(sentenced_text).dot(wrdvecs) # result is a matrix with 137 rows and 200 columns
print(vecr.transform(sentenced_text).toarray().shape)

# vecr.transform(sentenced_text) returns sparse matrix with 137 rows and 71291 columns
# it represents the counts of the words per sentence
# the dot command performs a matrix multiplication
# (137 x 71291) * (71291 x 200) = (137 x 200)
# the word counts of each of the 137 sentences are essentially element-wise multiplied with the corresponding word2vec matrix values
# and then summed up and this is done for every of the 200 dimensions
# so each sentence has a score for every dimension

# penalty is the minimum gain for a given number of max_splits
penalty = get_penalty([sentence_vectors], segment_len)
#print('penalty %4.2f' % penalty)

optimal_segmentation = split_optimal(sentence_vectors, penalty, seg_limit=250)
#print(optimal_segmentation)
segmented_text = get_segments(sentenced_text, optimal_segmentation)

#print('%d sentences, %d segments, avg %4.2f sentences per segment' % (
# len(sentenced_text), len(segmented_text), len(sentenced_text) / len(segmented_text)))

greedy_segmentation = split_greedy(sentence_vectors, max_splits=len(optimal_segmentation.splits))
#print(greedy_segmentation)
greedy_segmented_text = get_segments(sentenced_text, greedy_segmentation)
lengths_optimal = [len(segment) for segment in segmented_text for sentence in segment]
lengths_greedy = [len(segment) for segment in greedy_segmented_text for sentence in segment]

df = pd.DataFrame({'greedy':lengths_greedy, 'optimal': lengths_optimal})
df.plot.line(figsize=(18, 3), title='Segment lenghts over text')
#df.plot.hist(bins=30, alpha=0.5, figsize=(10, 3), title='Histogram of segment lengths')
# plt.show()

totals = [get_total(sentence_vectors, seg.splits, penalty) 
          for seg in [optimal_segmentation, greedy_segmentation]]
# print('optimal score %4.2f, greedy score %4.2f' % tuple(totals))
# print('ratio of scores %5.4f' % (totals[0] / totals[1])) 