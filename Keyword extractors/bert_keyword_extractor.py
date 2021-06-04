import sys
import os

# https://pypi.org/project/keybert/
from keybert import KeyBERT
from sklearn.feature_extraction.text import CountVectorizer
from nltk.corpus import stopwords
from sentence_transformers import SentenceTransformer

# add absolute path to main directory "summarization" to system paths
sys.path.insert(0, os.path.split(sys.path[0])[0])
path = sys.path[0]

# read sample file and create list of sentences
f = open(path + "/Keyword extractors/bbc_sample_text.txt", "r")
sentences = []
for line in f:
    sentences.append(line.strip("\n"))
# print(sentences)

keyphrase_ngram_range = (1, 2) # length of keyword (min, max)
n_keywords = 2 # number of keywords
use_mmr = True # enablse / disable diversity
diversity = 0.5 # the higher, the more diverse the keywords are [0, 1]

kw_extractor = KeyBERT("distilbert-base-nli-mean-tokens")
for sentence in sentences:
    keywords = kw_extractor.extract_keywords(sentence, keyphrase_ngram_range=keyphrase_ngram_range, top_n=n_keywords,
                                             diversity=diversity, use_mmr=use_mmr)
    print(keywords)


# https://towardsdatascience.com/keyword-extraction-with-bert-724efca412ea

# n_gram_range = (1, 2)
# stop_words = stopwords.words("english")

# # Extract candidate words/phrases
# count = CountVectorizer(ngram_range=n_gram_range, stop_words=stop_words).fit([sentences[2]])
# candidates = count.get_feature_names()
# #print(candidates)


# model = SentenceTransformer('distilbert-base-nli-mean-tokens')
# doc_embedding = model.encode([sentences[2]], )
# candidate_embeddings = model.encode(candidates)


# print(len(doc_embedding[0]))
# ###
# print(len(candidate_embeddings[0]))