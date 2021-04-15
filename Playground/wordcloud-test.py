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


print(transcript.head(5))
print()

transcript["Time"] = transcript["Time"].str.replace("60", "59")

stop_words = set(stopwords.words("english"))
stop_words.append("Thank", "Joe", "Biden", "Donald", "Trump", "America", "American")


text = ""
counter = 0
for t in transcript["Utterance"]:
    counter += 1
    text += " " + t
    if counter == 10:
        text += " " + t + "\n\n"
        counter = 0


ti = transcript.iloc[72, 1]
min = int(ti[0:2])

steps = 5
minutes = range(0, min, steps)
minutes = minutes[1:len(minutes)]

counter = 0
index_min = 0
for i in range(min):
    t = transcript[i,5]

for t in transcript["Utterance"]:
    if counter < minutes[index_min]:
        counter += 1
        text += " " + t
    else:
        index_min += 1
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
