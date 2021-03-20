import pandas as pd
import matplotlib.pyplot as plt
import string
import re
import math

import nltk
from nltk.corpus import stopwords, wordnet
from nltk.tokenize import word_tokenize
from wordcloud import WordCloud

from nltk.tokenize.api import TokenizerI

transcript = pd.read_csv(
        filepath_or_buffer="Playground\Vice presidential debate.csv",
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
#print(text)

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
        wrdindex_list.append((match.group(), match.start())) # list of tuples with word and word starting position
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

class TokenSequence(object):
    "A token list with its original length and its index"
    def __init__(self, index, wrdindex_list, original_length=None):
        original_length = original_length or len(wrdindex_list) # if no value is specified, len(wrdindex_list) is used
        self.__dict__.update(locals()) # make input variables to class variables (self.variable)
        del self.__dict__["self"] # delete self, otherwise self.self would be possible

# a = TokenSequence(1, ["a", "b", "c"]) # optional original_length argument
# print(a.index)
# print(a.wrdindex_list)
# print(a.original_length)
# # print(a.self)

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

### tokenize function

lowercase_text = text.lower()
paragraph_breaks = _mark_paragraph_breaks(text)
text_length = len(lowercase_text)
# print(paragraph_breaks); print(text_length)

## Tokenization step starts here

## Remove punctuation
nopunct_text = "".join(c for c in lowercase_text if re.match("[a-z\-' \n\t]", c)) # removes punctuation
nopunct_par_breaks = _mark_paragraph_breaks(nopunct_text)
# print(nopunct_par_breaks)

tokseqs = _divide_to_tokensequences(nopunct_text)

## Filter stopwords
for ts in tokseqs:
    ts.wrdindex_list = [wi for wi in ts.wrdindex_list if wi[0] not in stopwords]
# for ts in tokseqs:
#     print(ts.index, ts.wrdindex_list)

#### Why are stopwords filtered after pseudosentences are created?

token_table = _create_token_table(tokseqs, nopunct_par_breaks)
"""
word = "american"
print(token_table[word].first_pos) # position of first occurence of word
print(token_table[word].ts_occurences) # occurences in pseudosentences (token sequences)
print(token_table[word].total_count) # total word count
print(token_table[word].par_count) # total paragraph count (in how many paragraphs appeared it?)
print(token_table[word].last_par) # last paragraph of appearance
print(token_table[word].last_tok_seq) # last token sequence of appearance
"""

def blk_frq(tok, block):
    #print("tok ", tok)
    #print("block ", block)
    #print(token_table[tok].ts_occurences)
    ts_occs = filter(lambda o: o[0] in block, token_table[tok].ts_occurences) # checks if word occurs in the current block
    # for test in ts_occs:
    #     print("occ ", test)
    # print("sum ", sum([tsocc[1] for tsocc in ts_occs]))
    freq = sum([tsocc[1] for tsocc in ts_occs]) # sum of occurences in the current block
    #print("freq ", freq)
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
    print(b2)

    #counter = 0
    for t in token_table:
        # if counter > 20:
        #     break
        score_dividend += blk_frq(t, b1) * blk_frq(t, b2) # words must at least occur once in each block to obtain values > 0
        score_divisor_b1 += blk_frq(t, b1) ** 2
        score_divisor_b2 += blk_frq(t, b2) ** 2
        #counter += 1

    #print("score ", score_dividend)
    #print("divisor b1 ", score_divisor_b1)
    #print("divisor b2 ", score_divisor_b2)

    try:
        score = score_dividend / math.sqrt(score_divisor_b1 * score_divisor_b2)
    except ZeroDivisionError:
        pass  # score += 0.0

    gap_scores.append(score)

#print(gap_scores)




def _block_comparison(self, tokseqs, token_table):
        """Implements the block comparison method"""

        def blk_frq(tok, block):
            ts_occs = filter(lambda o: o[0] in block, token_table[tok].ts_occurences)
            freq = sum([tsocc[1] for tsocc in ts_occs])
            return freq

        gap_scores = []
        numgaps = len(tokseqs) - 1

        for curr_gap in range(numgaps):
            score_dividend, score_divisor_b1, score_divisor_b2 = 0.0, 0.0, 0.0
            score = 0.0
            # adjust window size for boundary conditions
            if curr_gap < self.k - 1:
                window_size = curr_gap + 1
            elif curr_gap > numgaps - self.k:
                window_size = numgaps - curr_gap
            else:
                window_size = self.k

            b1 = [ts.index for ts in tokseqs[curr_gap - window_size + 1 : curr_gap + 1]]
            b2 = [ts.index for ts in tokseqs[curr_gap + 1 : curr_gap + window_size + 1]]

            for t in token_table:
                score_dividend += blk_frq(t, b1) * blk_frq(t, b2) # words must at least occur once in each block to obtain values > 0
                score_divisor_b1 += blk_frq(t, b1) ** 2
                score_divisor_b2 += blk_frq(t, b2) ** 2
            try:
                score = score_dividend / math.sqrt(score_divisor_b1 * score_divisor_b2)
            except ZeroDivisionError:
                pass  # score += 0.0

            gap_scores.append(score)

        return gap_scores









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
