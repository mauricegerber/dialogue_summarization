import nltk
import pandas as pd
from nltk.corpus import stopwords, wordnet
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import datetime

transcript = pd.read_csv(
    filepath_or_buffer="Playground\Vice presidential debate.csv",
    header=0,
    names=["Speaker", "Time", "End time", "Duration", "Utterance"],
    usecols=["Speaker", "Time", "Utterance"],
)


transcript["Time"] = transcript["Time"].str.replace("60", "59")

stop_words = set(stopwords.words("english"))
stop_words |= set(["Thank", "Joe", "Biden", "Donald", "Trump", "America", "American", "President"])


nrow = len(transcript.index)-1

last_min = transcript.iloc[nrow, 1]
l_min = int(last_min[0:2])

steps = 5
minutes = range(0, l_min+steps, steps)
minutes = minutes[1:]


def analyse_minute(timestamp):
    minute = 0
    if len(timestamp) > 5:
        minute = 60 * int(timestamp[0:timestamp.find(":",0,len(timestamp))])
        timestamp = timestamp[timestamp.find(":",0,len(timestamp))+1:]
        
    minute += int(timestamp[0:timestamp.find(":",0,len(timestamp))])
    return(minute)


text = ""
index_min = 0
for i in range(nrow+1):
    t = transcript.iloc[i]["Utterance"]
    min_count = analyse_minute(transcript.iloc[i]["Time"])
    
    if min_count < minutes[index_min]:
        text += " " + t
      

    else:
        index_min += 1
        
        wordcloud = WordCloud(stopwords=stop_words).generate(text)
        plt.figure(figsize=(15,10))
        plt.clf()
        plt.imshow(wordcloud)
        plt.show()
        text = transcript.iloc[i]["Utterance"]

    if i == nrow:
        wordcloud = WordCloud(stopwords=stop_words).generate(text)
        plt.figure(figsize=(15,10))
        plt.clf()
        plt.imshow(wordcloud)
        plt.show()






# wordcloud = WordCloud(stopwords=stop_words).generate(text)

# plt.figure(figsize=(15,10))
# plt.clf()
# plt.imshow(wordcloud)
# plt.show()
