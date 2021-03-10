import pandas as pd
import yake
from yake import KeywordExtractor

df = pd.read_csv("./Test_Text.csv")

kw_extractor = yake.KeywordExtractor()
text = str(df)
language = "en"
max_ngram_size = 2 # length of Keywords
deduplication_threshold = 0.1 # limit the duplication of words in different keywords (0.9 = allowed, 0.1 = avoid)
numOfKeywords = 10 # number of keywords
custom_kw_extractor = yake.KeywordExtractor(lan=language, n=max_ngram_size, dedupLim=deduplication_threshold, top=numOfKeywords, features=None)
keywords = custom_kw_extractor.extract_keywords(text)
for kw in keywords:
	print(kw)