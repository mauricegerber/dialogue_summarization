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

ps = PorterStemmer()

transcript = pd.read_csv(
        filepath_or_buffer="Playground\Vice presidential debate.csv",
        #filepath_or_buffer="Playground\Job interview.csv",
        header=0,
        names=["Speaker", "Time", "End time", "Duration", "Utterance"],
        usecols=["Speaker", "Time", "Utterance"],
    )
transcript["Time"] = transcript["Time"].str.replace("60", "59")

text = ""
counter = 0
for t in transcript["Utterance"]:
    counter += 1
    text += " " + t
    if counter == 10:
        text += " " + t + "\n\n"
        counter = 0

def _mark_paragraph_breaks(text):
    "Identifies indented text or line breaks as the beginning of paragraphs"
    MIN_PARAGRAPH = 100 # min number of characters for paragraph
    pattern = re.compile("[ \t\r\f\v]*\n[ \t\r\f\v]*\n[ \t\r\f\v]*") # https://regex101.com/
    matches = pattern.finditer(text) # gets positions of line breaks in text
    last_break = 0
    pbreaks = [0]
    for pb in matches:
        if pb.start() - last_break < MIN_PARAGRAPH: # if next line break within MIN_PARAGRAPH, skip it
            continue
        else:
            pbreaks.append(pb.start())
            last_break = pb.start()
    return pbreaks # return list of line break positions in text

def _divide_to_tokensequences(text):
    "Divides the text into pseudosentences of fixed size"
    wrdindex_list = []
    matches = re.finditer("\w+", text) # gets positions of every word in text
    for match in matches:
        wrdindex_list.append((ps.stem(match.group()), match.start())) # list of tuples with word and word starting position
    return [TokenSequence(i / w, wrdindex_list[i : i + w]) for i in range(0, len(wrdindex_list), w)] # make an object of class TokenSequence
    # [(0.0, [('i', 1), ('m', 3), ('susan', 5), ('page', 11), ('of', 16), ('usa', 19), ('today', 23), ('it', 29), ('is', 32), ('my', 35), ('honor', 38), ('to', 44), ('moderate', 47), ('this', 56), ('debate', 61), ('an', 68), ('important', 71), ('part', 81), ('of', 86), ('our', 89)]),
    #  (1.0, [('democracy', 93), ('in', 103), ('kingsbury', 106), ('hall', 116), ('tonight', 121), ('we', 129), ('have', 132), ('a', 137), ('small', 139), ('and', 145), ('socially', 149), ('distant', 158), ('audience', 166), ('and', 175), ('we', 179), ('ve', 182), ('taken', 185), ('extra', 191), ('precautions', 197), ('during', 209)])]

def _create_token_table(token_sequences, par_breaks):
    "Creates a table of TokenTableFields"
    token_table = {}
    current_par = 0
    current_tok_seq = 0
    pb_iter = par_breaks.__iter__()
    current_par_break = next(pb_iter) # iterator currently set to index 0

    if current_par_break == 0:
        try:
            current_par_break = next(pb_iter) # iterator increased to index 1
        except StopIteration:
            raise ValueError("No paragraph breaks were found(text too short perhaps?)")
            # if the text has no paragraphs, this error raised
    
    for ts in token_sequences:
        for word, index in ts.wrdindex_list:
            try:
                while index > current_par_break:
                    current_par_break = next(pb_iter)
                    current_par += 1
            except StopIteration:
                # hit bottom, no more paragraphs
                pass

            if word in token_table: # check if word already appeared
                # print("existing word: ", word)
                token_table[word].total_count += 1

                if token_table[word].last_par != current_par:
                    token_table[word].last_par = current_par
                    token_table[word].par_count += 1

                if token_table[word].last_tok_seq != current_tok_seq:
                    token_table[word].last_tok_seq = current_tok_seq
                    token_table[word].ts_occurences.append([current_tok_seq, 1])
                else:
                    token_table[word].ts_occurences[-1][1] += 1

            else: # create new word if it did not appear yet
                token_table[word] = TokenTableField(
                    first_pos=index,
                    ts_occurences=[[current_tok_seq, 1]],
                    total_count=1,
                    par_count=1,
                    last_par=current_par,
                    last_tok_seq=current_tok_seq,
                )
                # print("new word: ", word)

        current_tok_seq += 1

    return token_table

def _block_comparison(tokseqs, token_table):
        """Implements the block comparison method"""
        def blk_frq(tok, block):
            # print("tok ", tok)
            # print("block ", block)
            # print(token_table[tok].ts_occurences)
            ts_occs = filter(lambda o: o[0] in block, token_table[tok].ts_occurences) # checks if word occurs in the current block
            freq = sum([tsocc[1] for tsocc in ts_occs]) # sum of occurences in the current block
            # print("freq ", freq)
            return freq

        gap_scores = []
        numgaps = len(tokseqs) - 1

        # test values range(7, 8)
        for curr_gap in range(numgaps):
            score_dividend, score_divisor_b1, score_divisor_b2 = 0.0, 0.0, 0.0
            score = 0.0
            # adjust window size for boundary conditions
            if curr_gap < k - 1:
                window_size = curr_gap + 1
            elif curr_gap > numgaps - k:
                window_size = numgaps - curr_gap
            else:
                window_size = k

            b1 = [ts.index for ts in tokseqs[curr_gap - window_size + 1 : curr_gap + 1]]
            b2 = [ts.index for ts in tokseqs[curr_gap + 1 : curr_gap + window_size + 1]]
            # windows are next to each other and max 10 elements long (parameter k)
            # every gap is once calculated
            # print(b1)

            # counter = 0
            for t in token_table:
                # if counter > 20:
                #     break
                # counter += 1
                score_dividend += blk_frq(t, b1) * blk_frq(t, b2) # words must at least occur once in each block to obtain values > 0
                score_divisor_b1 += blk_frq(t, b1) ** 2
                score_divisor_b2 += blk_frq(t, b2) ** 2

            #print("score ", score_dividend)
            #print("divisor b1 ", score_divisor_b1)
            #print("divisor b2 ", score_divisor_b2)

            try:
                score = score_dividend / math.sqrt(score_divisor_b1 * score_divisor_b2)
            except ZeroDivisionError:
                pass  # score += 0.0

            gap_scores.append(score)

        return gap_scores

def _smooth_scores(gap_scores):
    "Wraps the smooth function from the SciPy Cookbook"
    return list(
        smooth(np.array(gap_scores[:]), window_len=smoothing_width + 1)
    )

# Pasted from the SciPy cookbook: http://www.scipy.org/Cookbook/SignalSmooth
def smooth(x, window_len=11, window="flat"):
    "smooth the data using a window with requested size."
    if x.ndim != 1:
        raise ValueError("smooth only accepts 1 dimension arrays.")

    if x.size < window_len:
        raise ValueError("Input vector needs to be bigger than window size.")

    if window_len < 3:
        return x

    if window not in ["flat", "hanning", "hamming", "bartlett", "blackman"]:
        raise ValueError(
            "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"
        )

    s = np.r_[2 * x[0] - x[window_len:1:-1], x, 2 * x[-1] - x[-1:-window_len:-1]]

    # print(len(s))
    if window == "flat":  # moving average
        w = np.ones(window_len, "d")
    else:
        w = eval("np." + window + "(window_len)")

    y = np.convolve(w / w.sum(), s, mode="same")

    return y[window_len - 1 : -window_len + 1]

def _depth_scores(scores):
    """Calculates the depth of each gap, i.e. the average difference
    between the left and right peaks and the gap's score"""

    depth_scores = [0 for x in scores]
    # clip boundaries: this holds on the rule of thumb(my thumb)
    # that a section shouldn't be smaller than at least 2
    # pseudosentences for small texts and around 5 for larger ones.

    clip = min(max(len(scores) // 10, 2), 5)
    index = clip

    for gapscore in scores[clip:-clip]:
        # print(scores[clip:-clip])
        # print("gapscore ", gapscore)
        lpeak = gapscore
        for score in scores[index::-1]: # climbs up to the highest peak on the left starting from the current gapscore
            #print("left ", scores[index::-1])
            #print("score ", score)
            if score >= lpeak:
                #print(score, " >= ", lpeak)
                lpeak = score
                #print("new peak", lpeak)
            else:
                break
        rpeak = gapscore
        for score in scores[index:]: # climbs up to the highest peak on the right starting from the current gapscore
            # print("right ", scores[index:])
            # print("right ", score)
            if score >= rpeak:
                # print(score, " >= ", rpeak)
                rpeak = score
                # print("new peak", rpeak)
            else:
                break
        depth_scores[index] = lpeak + rpeak - 2 * gapscore
        index += 1
    
    return depth_scores

def _identify_boundaries(depth_scores):
    """Identifies boundaries at the peaks of similarity score
    differences"""

    boundaries = [0 for x in depth_scores]

    avg = sum(depth_scores) / len(depth_scores)
    stdev = np.std(depth_scores)
    # print(avg) ;print(stdev)

    cutoff = avg - stdev / 2.0
    # print(cutoff)

    depth_tuples = sorted(zip(depth_scores, range(len(depth_scores))))
    depth_tuples.reverse()
    hp = list(filter(lambda x: x[0] > cutoff, depth_tuples))

    for dt in hp:
        boundaries[dt[1]] = 1
        for dt2 in hp:  # undo if there is a boundary close already
            if (
                dt[1] != dt2[1]
                and abs(dt2[1] - dt[1]) < 4
                and boundaries[dt2[1]] == 1
            ):
                boundaries[dt[1]] = 0
    return boundaries

def _normalize_boundaries(text, boundaries, paragraph_breaks):
    """Normalize the boundaries identified to the original text's
    paragraph breaks"""

    norm_boundaries = []
    char_count, word_count, gaps_seen = 0, 0, 0
    seen_word = False

    for char in text:
        char_count += 1
        # print("char ", char)
        if char in " \t\n" and seen_word:
            # print("first if")
            seen_word = False
            word_count += 1
        if char not in " \t\n" and not seen_word:
            # print("second if")
            seen_word = True
        if gaps_seen < len(boundaries) and word_count > (max(gaps_seen * w, w)): # gap between token sequences
            # print("third if")
            # print("boundaries at gaps_seen ", boundaries[gaps_seen])
            if boundaries[gaps_seen] == 1:
                # find closest paragraph break
                best_fit = len(text)
                for br in paragraph_breaks:
                    if best_fit > abs(br - char_count):
                        # print("current best_fit ", best_fit)
                        best_fit = abs(br - char_count)
                        # print("new best_fit",best_fit)
                        bestbr = br
                        # print("best break", br)
                    else:
                        break
                if bestbr not in norm_boundaries:  # avoid duplicates
                    norm_boundaries.append(bestbr)
            gaps_seen += 1

    return norm_boundaries

class TokenSequence(object):
    "A token list with its original length and its index"
    def __init__(self, index, wrdindex_list, original_length=None):
        original_length = original_length or len(wrdindex_list) # if no value is specified, len(wrdindex_list) is used
        self.__dict__.update(locals()) # make input variables to class variables (self.variable)
        del self.__dict__["self"] # delete self, otherwise self.self would be possible

# a = TokenSequence(1, ["a", "b", "c"]) # optional original_length argument
# b = [1, ["a", "b", "c"]]
# print(b[0])
# print(a.index)
# print(a.wrdindex_list)
# print(a.original_length)
# print(a.self)

class TokenTableField(object):
    """A field in the token table holding parameters for each token,
    used later in the process"""
    def __init__(
        self,
        first_pos,
        ts_occurences,
        total_count=1,
        par_count=1,
        last_par=0,
        last_tok_seq=None,
    ):
        self.__dict__.update(locals())
        del self.__dict__["self"]

### Hyperparameters

w = 20
k = 10
stopwords = stopwords.words("english")
#print(stopwords)
smoothing_width=2
#smoothing_rounds=1,

### tokenize function

#text = brown.raw()[:10000]
#print(text)

lowercase_text = text.lower()
paragraph_breaks = _mark_paragraph_breaks(text)
text_length = len(lowercase_text)
print(paragraph_breaks) # [0, 8514, 11393, 19021, 26556, 32490, 39524, 45601]
# print(text_length) 

## Tokenization step starts here

## Remove punctuation
nopunct_text = "".join(c for c in lowercase_text if re.match("[a-z\-' \n\t]", c)) # removes punctuation
nopunct_par_breaks = _mark_paragraph_breaks(nopunct_text)
# print(nopunct_par_breaks)
# print(nopunct_text)

tokseqs = _divide_to_tokensequences(nopunct_text)

## Filter stopwords
for ts in tokseqs:
    ts.wrdindex_list = [wi for wi in ts.wrdindex_list if wi[0] not in stopwords]

token_table = _create_token_table(tokseqs, nopunct_par_breaks)
# word = "health"
# print(token_table[word].first_pos) # position of first occurence of word
# print(token_table[word].ts_occurences) # occurences in pseudosentences (token sequences)
# print(token_table[word].total_count) # total word count
# print(token_table[word].par_count) # total paragraph count (in how many paragraphs appeared it?)
# print(token_table[word].last_par) # last paragraph of appearance
# print(token_table[word].last_tok_seq) # last token sequence of appearance


## Lexical score determination
gap_scores = _block_comparison(tokseqs, token_table)
# print(gap_scores)

smooth_scores = _smooth_scores(gap_scores)
# print(smooth_scores)
# plt.plot(range(len(gap_scores)), gap_scores)
plt.plot(range(len(smooth_scores)), smooth_scores)

## Boundary identification
depth_scores = _depth_scores(smooth_scores)

# test = [i for i in range(30)]
# print(test) # [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29]
# print(test[clip:-clip]) # [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
# print(test[index::-1]) # [5, 4, 3, 2, 1, 0]

# print(depth_scores)
plt.plot(range(len(depth_scores)), depth_scores)
plt.show()

segment_boundaries = _identify_boundaries(depth_scores)
# print(segment_boundaries)

normalized_boundaries = _normalize_boundaries(text, segment_boundaries, paragraph_breaks)
#print(normalized_boundaries)

segmented_text = []
prevb = 0

for b in normalized_boundaries:
    if b == 0:
        continue
    segmented_text.append(text[prevb:b])
    prevb = b

if prevb < text_length:  # append any text that may be remaining
    segmented_text.append(text[prevb:])

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
