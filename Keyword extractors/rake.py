import sys
import os

from rake_nltk import Rake

# add absolute path to main directory "summarization" to system paths
sys.path.insert(0, os.path.split(sys.path[0])[0])

# read sample file and create list of sentences
f = open("./Keyword extractors/bbc_sample_text.txt", "r")
sentences = []
for line in f:
    sentences.append(line.strip("\n"))
# print(sentences)

for sentence in sentences:
    r = Rake() # Uses stopwords for english from NLTK, and all puntuation characters.
    r.extract_keywords_from_text(sentence)
    print(r.get_ranked_phrases()) # To get keyword phrases ranked highest to lowest.
