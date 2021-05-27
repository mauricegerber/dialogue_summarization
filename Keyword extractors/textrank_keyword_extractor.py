import sys
import os

# https://github.com/summanlp/textrank
from summa import keywords

# add absolute path to main directory "summarization" to system paths
sys.path.insert(0, os.path.split(sys.path[0])[0])

# read sample file and create list of sentences
f = open("./Keyword extractors/bbc_sample_text.txt", "r")
sentences = []
for line in f:
    sentences.append(line.strip("\n"))
# print(sentences)

for sentence in sentences:
    kws = keywords.keywords(sentence, words=5)
    print(kws)
