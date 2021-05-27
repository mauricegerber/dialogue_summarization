import sys
import os

# https://pypi.org/project/keybert/
from keybert import KeyBERT

# add absolute path to main directory "summarization" to system paths
sys.path.insert(0, os.path.split(sys.path[0])[0])

# read sample file and create list of sentences
f = open("./Keyword extractors/bbc_sample_text.txt", "r")
sentences = []
for line in f:
    sentences.append(line.strip("\n"))
# print(sentences)

keyphrase_ngram_range = (1, 1) # length of keyword (min, max)
n_keywords = 5 # number of keywords
use_mmr = True # enablse / disable diversity
diversity = 1 # the higher, the more diverse the keywords are [0, 1]

kw_extractor = KeyBERT("distilbert-base-nli-mean-tokens")
for sentence in sentences:
    keywords = kw_extractor.extract_keywords(sentence, keyphrase_ngram_range=keyphrase_ngram_range, top_n=n_keywords,
                                             diversity=diversity, use_mmr=use_mmr)
    print(keywords)
