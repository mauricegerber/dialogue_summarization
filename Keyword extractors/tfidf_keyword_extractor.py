import sys
import os
import pandas as pd

# add absolute path to main directory "summarization" to system paths
sys.path.insert(0, os.path.split(sys.path[0])[0])
path = sys.path[0]

# https://en.wikipedia.org/wiki/Tf%E2%80%93idf
from Dash.functions.tfidf import tfidf

# read sample file and create list of sentences
f = open(path + "/Keyword extractors/bbc_sample_text.txt", "r")
sentences = []
for line in f:
    sentences.append(line.strip("\n"))
# print(sentences)

pd.set_option("display.max_rows", 1000)
df = tfidf(sentences)
print(df)
