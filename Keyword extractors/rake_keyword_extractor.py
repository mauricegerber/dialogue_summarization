import sys
import os

# https://pypi.org/project/rake-nltk/
from rake_nltk import Rake

# add absolute path to main directory "summarization" to system paths
sys.path.insert(0, os.path.split(sys.path[0])[0])
path = sys.path[0]

# read sample file and create list of sentences
f = open(path + "/Keyword extractors/bbc_sample_text.txt", "r")
sentences = []
for line in f:
    sentences.append(line.strip("\n"))
# print(sentences)

r = Rake() # Uses stopwords for english from NLTK, and all puntuation characters.
for sentence in sentences:
    r.extract_keywords_from_text(sentence)
    print(r.get_ranked_phrases()) # To get keyword phrases ranked highest to lowest.
