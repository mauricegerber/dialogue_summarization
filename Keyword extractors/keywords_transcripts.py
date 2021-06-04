import sys
import os
import pandas as pd
import time

sys.path.insert(0, os.path.split(sys.path[0])[0])
path = sys.path[0]

from nltk.corpus import stopwords
from rake_nltk import Rake
from yake import KeywordExtractor
from keybert import KeyBERT
from Dash.functions.tfidf import tfidf

# Vice presidential debate.csv
# BA meeting 2021-03-11.csv
transcripts_dir = path + "/Dash/transcripts/"
transcript = pd.read_csv(
    filepath_or_buffer=transcripts_dir + "BA meeting 2021-03-11.csv",
    header=0,
    names=["Speaker", "Time", "End time", "Duration", "Utterance"],
    usecols=["Speaker", "Time", "Utterance"]
)

# TF-IDF
transcript_files = ["BA meeting 2021-03-11.csv", "BA meeting 2021-03-25.csv", "BA meeting 2021-04-23.csv", "BA meeting 2021-05-07.csv"]
transcripts = []
texts = []
for file in transcript_files:
    text = ""
    transcript = pd.read_csv(
        filepath_or_buffer=transcripts_dir + file,
        header=0,
        names=["Speaker", "Time", "End time", "Duration", "Utterance"],
        usecols=["Speaker", "Time", "Utterance"]
    )
    for utterance in transcript["Utterance"]:
        text = text + utterance.lower() + " "
    texts.append(text)

start_time = time.time()
df = tfidf(texts)
print("--- %s seconds ---" % (time.time() - start_time))

df.to_csv(path + "/Keyword extractors/temp.csv")


# # KeyBERT
# text = ""
# for utterance in transcript["Utterance"]:
#     text = text + utterance + " "

# sw = stopwords.words("german")
# start_time = time.time()
# kw_extractor = KeyBERT("distilbert-base-nli-mean-tokens")
# keywords = kw_extractor.extract_keywords(text, stop_words=sw, keyphrase_ngram_range=(1,3), top_n=3, diversity=0, use_mmr=True)
# print("--- %s seconds ---" % (time.time() - start_time))
# print(keywords)

# # YAKE
# text = ""
# for utterance in transcript["Utterance"]:
#     text = text + utterance + " "

# start_time = time.time()
# kw_extractor = KeywordExtractor(lan="de", n=3, top=3, dedupLim=0)
# keywords = kw_extractor.extract_keywords(text)
# print("--- %s seconds ---" % (time.time() - start_time))
# print(keywords)

# # RAKE
# text = ""
# for utterance in transcript["Utterance"]:
#     text = text + utterance.lower() + " "

# sw = stopwords.words("german")
# start_time = time.time()
# r = Rake(stopwords=sw)
# r.extract_keywords_from_text(text)
# print("--- %s seconds ---" % (time.time() - start_time))
# print(r.get_ranked_phrases_with_scores())
