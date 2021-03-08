import pandas as pd

from summa import keywords
from pytopicrank import TopicRank



transcript = pd.read_csv("C:\\Users\\pasca\\myCloud\\01 Studium\\ZHAW\\Bachelor Wirtschaftsingenieurwesen\\6. Semester\\BA\\summarization\\Dash\\us_election_2020_vice_presidential_debate.csv")


transcript_filtered = transcript[transcript.speaker.isin(transcript.speaker.unique()[:2])]

print(transcript_filtered.head(20))