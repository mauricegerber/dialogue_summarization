import nltk
import pandas as pd
from nltk.corpus import stopwords, wordnet
from wordcloud import WordCloud
import matplotlib.pyplot as plt

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


text = ""
counter = 0
for t in transcript["Utterance"]:
    counter += 1
    text += " " + t
    if counter == 10:
        text += " " + t + "\n\n"
        counter = 0

print(transcript["Time"])


wordcloud = WordCloud(stopwords=stop_words).generate(text)

plt.figure(figsize=(15,10))
plt.clf()
plt.imshow(wordcloud)
plt.show()
