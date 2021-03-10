import pandas as pd
import yake
from yake import KeywordExtractor

df = pd.read_csv("./Test_Text.csv", usecols = ["text"])
df = df[:100]
print(df)

kw_extractor = yake.KeywordExtractor()
language = "en"
max_ngram_size = 1 # length of Keywords
deduplication_threshold = 0.1 # limit the duplication of words in different keywords (0.9 = allowed, 0.1 = avoid)
numOfKeywords = 3 # number of keywords

kw_extractor = yake.KeywordExtractor(lan=language, n=max_ngram_size, 
	dedupLim=deduplication_threshold, top=numOfKeywords, features=None)


for j in range(len(df)):
    keywords = kw_extractor.extract_keywords(text=df["text"][j])
    print("Keywords of row", str(j+1), "\n", keywords)

