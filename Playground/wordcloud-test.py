import nltk
import pandas as pd
from nltk.corpus import stopwords, wordnet
from wordcloud import (WordCloud, get_single_color_func)
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import matplotlib.pyplot as plt
import datetime

import random
import sys
import os
sys.path.insert(0, os.path.split(os.path.split(sys.path[0])[0])[0])

pio.kaleido.scope.default_format = "png"
pio.kaleido.scope.default_width = 1920
pio.kaleido.scope.default_height = 500

transcript = pd.read_csv(
    filepath_or_buffer="Playground\Vice presidential debate.csv",
    header=0,
    names=["Speaker", "Time", "End time", "Duration", "Utterance"],
    usecols=["Speaker", "Time", "Utterance"],
)


transcript["Time"] = transcript["Time"].str.replace("60", "59")

stop_words = set(stopwords.words("english"))
stop_words |= set(["Thank", "Joe", "Biden", "Donald", "Trump", "America", "American", "President", "Harris", "I'm", "would", "know", "we're", "one", "two", "three", "four",
"first", "said", "going", "say", "think", "go", "made"])
sw_lower = [each_string.lower() for each_string in stop_words]

class GroupedColorFunc(object):
    """Create a color function object which assigns DIFFERENT SHADES of
       specified colors to certain words based on the color to words mapping.
       Uses wordcloud.get_single_color_func
       Parameters
       ----------
       color_to_words : dict(str -> list(str))
         A dictionary that maps a color to the list of words.
       default_color : str
         Color that will be assigned to a word that's not a member
         of any value from color_to_words.
    """

    def __init__(self, color_to_words, default_color):
        self.color_func_to_words = [
            (get_single_color_func(color), set(words))
            for (color, words) in color_to_words.items()]

        self.default_color_func = get_single_color_func(default_color)

    def get_color_func(self, word):
        """Returns a single_color_func associated with the word"""
        try:
            color_func = next(
                color_func for (color_func, words) in self.color_func_to_words
                if word in words)
        except StopIteration:
            color_func = self.default_color_func

        return color_func

    def __call__(self, word, **kwargs):
        return self.get_color_func(word)(word, **kwargs)



nrow = len(transcript.index)-1

last_min = transcript.iloc[nrow, 1]
l_min = int(last_min[0:2])

steps = 5 # Time steps adjustment in minutes
minutes = range(0, l_min+steps, steps)
minutes = minutes[1:]


def analyse_minute(timestamp):
    minute = 0
    if len(timestamp) > steps:
        minute = 60 * int(timestamp[0:timestamp.find(":",0,len(timestamp))])
        timestamp = timestamp[timestamp.find(":",0,len(timestamp))+1:]
        
    minute += int(timestamp[0:timestamp.find(":",0,len(timestamp))])
    return(minute)

def compare_wordlist(text_old, text_new):
    w_old_normal = text_old.split()
    w_new_normal = text_new.split()
    w_old = [each_string.lower() for each_string in w_old_normal]
    w_new = [each_string.lower() for each_string in w_new_normal]
    words_old = [x for x in w_old + w_new if x not in w_new and x not in sw_lower]
    words_new = [x for x in w_old + w_new if x not in w_old and x not in sw_lower]
    return words_old, words_new

def create_wordcloud(text, words_old, words_new, key):
    color_to_words = {
        # words below will be colored with a green single color function
        '#00ff00': words_new,
        # will be colored with a red single color function
        'red': words_old
    }        
    
    default_color = "black"
    grouped_color_func = GroupedColorFunc(color_to_words, default_color)

    wordcloud = WordCloud(stopwords=stop_words, collocations=False, max_words = 15, 
    background_color='white', width=1920, height=1000).generate(text.lower())
    wordcloud.recolor(color_func=grouped_color_func)

    plt.figure(figsize=(15,10))
    plt.clf()
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.savefig("./images in paper/Wordcloud/wordcloud_p1{}.png".format(key), dpi = 300)



text = ""
text_old = ""
index_min = 0
for i in range(nrow+1):
    t = transcript.iloc[i]["Utterance"]
    min_count = analyse_minute(transcript.iloc[i]["Time"])
    
    if min_count < minutes[index_min]:
        text += " " + t

    else:
        index_min += 1
        co_wo = compare_wordlist(text_old, text)
        
        create_wordcloud(text, co_wo[0], co_wo[1], index_min-1)
        text_old = text
        text = transcript.iloc[i]["Utterance"]

    if i == nrow:
        co_wo = compare_wordlist(text_old, text)
        create_wordcloud(text, co_wo[0], co_wo[1], index_min)


# a = ["a", "Basil", "cool", "Cool", "harris"]
# b = ["A", "President", "Cool", "yey", "harris"]
# sw = set(["a", "Harris", "president"])
# wold = [x for x in a + b if x not in b and x not in sw]
# wnew = [x for x in a + b if x not in a and x not in sw]

# a = [each_string.lower() for each_string in a]
# print(a)

# text = ""
# for t in transcript[1:5]["Utterance"]:
#     text += " " + t
# print(type(text))

# te = ""
# a = text.split()
# print(len(a))

# a1 = te.split()
# a2 = a
# sswords = ["that", "is"]
# words_old = [x for x in a1 + a2 if x not in a2 and x not in sswords]
# words_new = [x for x in a1 + a2 if x not in a1 and x not in sswords]

# print(words_old)
# print(words_new)

# color_to_words = {
#         # words below will be colored with a green single color function
#         '#00ff00': words_new,
#         # will be colored with a red single color function
#         'red': words_old
#     }        
    
# default_color = "grey"
# grouped_color_func = GroupedColorFunc(color_to_words, default_color)

# wordcloud = WordCloud(stopwords=stop_words,collocations=False).generate(text)
# wordcloud.recolor(color_func=grouped_color_func)

# plt.figure(figsize=(15,10))
# plt.clf()
# plt.imshow(wordcloud, interpolation="bilinear")
# plt.show()