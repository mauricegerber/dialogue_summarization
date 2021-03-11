import pandas as pd

from keybert import KeyBERT


#transcript = pd.read_csv("C:\\Users\\basil\\myCloud\\01 Studium\\ZHAW\\Bachelor Wirtschaftsingenieurwesen\\6. Semester\\BA\\summarization\\Dash\\us_election_2020_vice_presidential_debate.csv")

transcript = pd.read_csv("C:\\Users\\basil\\Documents\\summarization\\summarization\\Dash\\us_election_2020_vice_presidential_debate.csv")
kw_extractor = KeyBERT('distilbert-base-nli-mean-tokens')

kw_extractor = KeyBERT('distilbert-base-nli-mean-tokens')
for j in range(len(transcript)):
    try:
        keywords = kw_extractor.extract_keywords(transcript["text"][j], keyphrase_ngram_range=(1,3), stop_words = "english", diversity=0.7, use_mmr=True)
        # Keyprhase range = min/max number of words
        # For using diversity parameter, use_mmr=True is needed
        print(keywords)
    except:
        print("empty")

