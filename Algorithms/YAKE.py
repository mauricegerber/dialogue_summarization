import pandas as pd
import yake
from yake import KeywordExtractor

df = pd.read_csv("./us_election_2020_1st_presidential_debate.csv")

kw_extractor = yake.KeywordExtractor()
text = str(df)
