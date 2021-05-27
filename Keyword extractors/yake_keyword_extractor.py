import sys
import os

# https://github.com/LIAAD/yake
from yake import KeywordExtractor

# add absolute path to main directory "summarization" to system paths
sys.path.insert(0, os.path.split(sys.path[0])[0])
path = sys.path[0]

# read sample file and create list of sentences
f = open(path + "/Keyword extractors/bbc_sample_text.txt", "r")
sentences = []
for line in f:
    sentences.append(line.strip("\n"))
# print(sentences)

language = "en"
max_ngram_size = 1 # length of keyword
n_keywords = 5 # number of keywords
deduplication_threshold = 0.1 # limit the duplication of words in different keywords (0.9 = allowed, 0.1 = avoid)

kw_extractor = KeywordExtractor(lan=language, n=max_ngram_size, top=n_keywords, dedupLim=deduplication_threshold)
for sentence in sentences:
    keywords = kw_extractor.extract_keywords(sentence)
    print(keywords)
