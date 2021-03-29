import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import string
import re
import math

import nltk
from nltk.corpus import stopwords#, wordnet, brown
from nltk.tokenize import word_tokenize
#from wordcloud import WordCloud
from nltk.stem import PorterStemmer

#from nltk.tokenize.api import TokenizerI

transcript = pd.read_csv(
        filepath_or_buffer="Playground\Vice presidential debate.csv",
        #filepath_or_buffer="Playground\Job interview.csv",
        header=0,
        names=["Speaker", "Time", "End time", "Duration", "Utterance"],
        usecols=["Speaker", "Time", "Utterance"],
    )
transcript["Time"] = transcript["Time"].str.replace("60", "59")

### Hyperparameters
w = 20
k = 10
stopwords = stopwords.words("english")
# print(stopwords)
smoothing_width=2

##########

text = ""
utterance_break = 0
utterance_breaks = []
for utterance in transcript["Utterance"].str.lower():
    text += utterance
    utterance_break += len(utterance)
    utterance_breaks.append(utterance_break)
print(utterance_breaks)
# print(text)

class TokenSequence(object):
    def __init__(self, index, word_list):
        self.__dict__.update(locals())
        del self.__dict__["self"]

def divide_to_token_sequences(text):
    """Divides the text into pseudosentences of fixed size."""
    word_list = []
    matches = re.finditer("\w+", text)
    for match in matches:
        word_list.append((match.group(), match.start()))
    return [TokenSequence(int(i / w), word_list[i : i + w]) for i in range(0, len(word_list), w)]

tokseqs = divide_to_token_sequences(text)
# for ts in tokseqs:
#     print(ts.index, ts.word_list)

for ts in tokseqs:
    ts.word_list = [wi for wi in ts.word_list if wi[0] not in stopwords]
    # print(ts.index, ts.word_list)

stemmer = PorterStemmer()
for ts in tokseqs:
    ts.word_list = [(stemmer.stem(w), i) for w, i in ts.word_list]
    # print(ts.index, ts.word_list)

class TokenTable(object):
    def __init__(self, total_count, ts_occurrences, last_ts):
        self.__dict__.update(locals())
        del self.__dict__["self"]

def create_token_table(token_sequences):
    """Creates a table of TokenTable."""
    token_table = {}
    current_ts = 0
    for ts in token_sequences:
        for word, index in ts.word_list:
            if word in token_table:
                token_table[word].total_count += 1
                if token_table[word].last_ts != current_ts:
                    token_table[word].last_ts = current_ts
                    token_table[word].ts_occurrences.append([current_ts, 1])
                else:
                    token_table[word].ts_occurrences[-1][1] += 1
            else:
                token_table[word] = TokenTable(
                    total_count=1,
                    ts_occurrences=[[current_ts, 1]],
                    last_ts=current_ts,
                )
        current_ts += 1
    return token_table

token_table = create_token_table(tokseqs)
# word = "health"
# print(token_table[word].total_count)
# print(token_table[word].ts_occurrences)
# print(token_table[word].last_ts)

def block_comparison(token_sequences, token_table):
    """Implements the block comparison method."""
    def blk_frq(tok, block):
        ts_occs = filter(lambda o: o[0] in block, token_table[tok].ts_occurrences)
        freq = sum([tsocc[1] for tsocc in ts_occs])
        return freq
    
    gap_scores = []
    n_gaps = len(token_sequences) - 1

    for current_gap in range(n_gaps):
        score_dividend, score_divisor_b1, score_divisor_b2 = 0.0, 0.0, 0.0
        # adjust window size for boundary conditions
        if current_gap < k - 1:
            window_size = current_gap + 1
        elif current_gap > n_gaps - k:
            window_size = n_gaps - current_gap
        else:
            window_size = k
        b1 = [ts.index for ts in token_sequences[current_gap - window_size + 1 : current_gap + 1]]
        b2 = [ts.index for ts in token_sequences[current_gap + 1 : current_gap + window_size + 1]]
        for t in token_table:
            score_dividend += blk_frq(t, b1) * blk_frq(t, b2)
            score_divisor_b1 += blk_frq(t, b1) ** 2
            score_divisor_b2 += blk_frq(t, b2) ** 2
        try:
            score = score_dividend / math.sqrt(score_divisor_b1 * score_divisor_b2)
        except ZeroDivisionError:
            pass
        gap_scores.append(score)
    
    return gap_scores

gap_scores = block_comparison(tokseqs, token_table)
# print(gap_scores)
# plt.plot(range(len(gap_scores)), gap_scores)
# plt.show()

def calculate_depth_scores(scores):
    """Calculates the depth of each gap, i.e. the average difference
    between the left and right peak and the gap's score."""
    depth_scores = [0 for x in scores]
    clip = 5
    index = clip
    for gapscore in scores[clip:-clip]:
        lpeak = gapscore
        for score in scores[index::-1]:
            if score >= lpeak:
                lpeak = score
            else:
                break
        rpeak = gapscore
        for score in scores[index:]:
            if score >= rpeak:
                rpeak = score
            else:
                break
        depth_scores[index] = lpeak + rpeak - 2 * gapscore
        index += 1
    return depth_scores

depth_scores = calculate_depth_scores(gap_scores)
# print(depth_scores)
# plt.plot(range(len(depth_scores)), depth_scores)
# plt.show()

def identify_boundaries(depth_scores):
    """Identifies boundaries at the peaks of similarity score differences."""
    boundaries = [0 for x in depth_scores]
    # mean = np.mean(depth_scores)
    # sd = np.std(depth_scores)
    # cutoff = mean - sd / 2.0
    cutoff = 0.3

    depth_tuples = zip(depth_scores, range(len(depth_scores)))
    hp = filter(lambda x: x[0] > cutoff, depth_tuples)
    boundaries = sorted([i for value, i in hp])

    removed_boundaries = []
    for i in range(1, len(boundaries)):
        if boundaries[i] < boundaries[i-1] + 10:
            removed_boundaries.append(boundaries[i])
    boundaries = [b for b in boundaries if b not in removed_boundaries]

    return boundaries

boundaries = identify_boundaries(depth_scores)
print(boundaries)

utterance_breaks_boundaries = []
for ts in tokseqs:
    if ts.index+1 in boundaries:
        utterance_breaks_boundaries.append(ts.word_list[-1][1])

print(utterance_breaks_boundaries)

# utterance_segments = []
# for i in range(len(utterance_breaks)):







#normalized_boundaries = _normalize_boundaries(text, segment_boundaries, paragraph_breaks)
#print(normalized_boundaries)

# segmented_text = []
# prevb = 0

# for b in normalized_boundaries:
#     if b == 0:
#         continue
#     segmented_text.append(text[prevb:b])
#     prevb = b

# if prevb < text_length:  # append any text that may be remaining
#     segmented_text.append(text[prevb:])

# if not segmented_text:
#     segmented_text = [text]

# if self.demo_mode:
#     return gap_scores, smooth_scores, depth_scores, segment_boundaries
# return segmented_text

#print(text)
#print()
#print(segmented_text[1])






# from nltk.corpus import brown
# tt = nltk.tokenize.texttiling.TextTilingTokenizer(demo_mode=True)
# text = brown.raw()[:10000]

# print(text)

# s, ss, d, b = tt.tokenize(text)
# print(s)
# print()
# print(ss)
# print()
# print(d)
# print()
# print(b)















# print(transcript.head(5))
# print()

# text = ""
# for utterance in transcript["Utterance"]:
#     text += " " + utterance.lower()

# print(text[:300])
# print()

# words = word_tokenize(text)

# print(words[:100])
# print()

# stop_words = set(stopwords.words("english") + list(string.punctuation))

# filtered_words = []
# for w in words:
#     if w not in stop_words:
#         filtered_words.append(w)

# print(filtered_words[:100])
# print()

# w1 = wordnet.synset("corona.n.01")
# values = []
# for w in filtered_words:
#     try:
#         w2 = wordnet.synset(w + ".n.01")
#         values.append(w1.wup_similarity(w2))
#     except:
#         values.append(0)

# #print(values)

# m = max(values)
# indices = [i for i, j in enumerate(values) if j == m]
# print(indices)

# print(filtered_words[indices[0]])
# print(filtered_words[indices[1]])

# plt.plot(values)
# # plt.show()

# wordcloud = WordCloud(stopwords=stop_words).generate(text)

# plt.figure(figsize=(15,10))
# plt.clf()
# plt.imshow(wordcloud)
# plt.show()
