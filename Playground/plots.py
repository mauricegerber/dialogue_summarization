import pandas as pd
import matplotlib.pyplot as plt
import string

from nltk.corpus import stopwords, wordnet
from nltk.tokenize import word_tokenize
from wordcloud import WordCloud

transcript = pd.read_csv(
        filepath_or_buffer="Playground\Vice presidential debate.csv",
        header=0,
        names=["Speaker", "Time", "End time", "Duration", "Utterance"],
        usecols=["Speaker", "Time", "Utterance"],
    )
transcript["Time"] = transcript["Time"].str.replace("60", "59")

print(transcript.head(5))
print()

text = ""
for utterance in transcript["Utterance"]:
    text += " " + utterance.lower()

print(text[:300])
print()

words = word_tokenize(text)

print(words[:100])
print()

stop_words = set(stopwords.words("english") + list(string.punctuation))

filtered_words = []
for w in words:
    if w not in stop_words:
        filtered_words.append(w)

print(filtered_words[:100])
print()

w1 = wordnet.synset("corona.n.01")
values = []
for w in filtered_words:
    try:
        w2 = wordnet.synset(w + ".n.01")
        values.append(w1.wup_similarity(w2))
    except:
        values.append(0)

#print(values)

m = max(values)
indices = [i for i, j in enumerate(values) if j == m]
print(indices)

print(filtered_words[indices[0]])
print(filtered_words[indices[1]])

plt.plot(values)
# plt.show()

wordcloud = WordCloud(stopwords=stop_words).generate(text)

plt.figure(figsize=(15,10))
plt.clf()
plt.imshow(wordcloud)
plt.show()

