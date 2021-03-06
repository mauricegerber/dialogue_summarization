import pandas as pd

from summa import keywords
from pytopicrank import TopicRank



transcript = pd.read_csv("C:\\Users\\pasca\\myCloud\\01 Studium\\ZHAW\\Bachelor Wirtschaftsingenieurwesen\\6. Semester\\BA\\summarization\\Dash\\us_election_2020_vice_presidential_debate.csv")
transcript = transcript[:10]

kws = [None] * len(transcript)

for i in range(len(transcript)):
    #kws[i] = keywords.keywords(transcript["text"][i])

    try:
        tr = TopicRank(transcript["text"][i])
        kws[i] = ", ".join(tr.get_top_n(3))
    except:
        kws[i] = ""

    print(kws[i])


transcript["textrank"] = kws
print(transcript)

