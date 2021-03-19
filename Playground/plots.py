import pandas as pd
import matplotlib.pyplot as plt
import string

import nltk
from nltk.corpus import stopwords, wordnet
from nltk.tokenize import word_tokenize
from wordcloud import WordCloud

from nltk.tokenize.api import TokenizerI

transcript = pd.read_csv(
        filepath_or_buffer="Playground\Vice presidential debate.csv",
        header=0,
        names=["Speaker", "Time", "End time", "Duration", "Utterance"],
        usecols=["Speaker", "Time", "Utterance"],
    )
transcript["Time"] = transcript["Time"].str.replace("60", "59")

text = ""
counter = 0
for t in transcript["Utterance"]:
    counter += 1
    text += " " + t
    if counter == 10:
        text += " " + t + "\n\n"
        counter = 0

    
# print(text)

from nltk.corpus import brown
tt = nltk.tokenize.texttiling.TextTilingTokenizer(demo_mode=True)
text = brown.raw()[:10000]

#print(text)

s, ss, d, b = tt.tokenize(text)
print(s)
print()
print(ss)
print()
print(d)
print()
print(b)






# print(transcript.head(5))
# print()

# text = ""
# for utterance in transcript["Utterance"]:
#     text += " " + utterance.lower()

# print(text[:300])
# print()

# words = word_tokenize(text)

# print(words[:100])
# print()

# stop_words = set(stopwords.words("english") + list(string.punctuation))

# filtered_words = []
# for w in words:
#     if w not in stop_words:
#         filtered_words.append(w)

# print(filtered_words[:100])
# print()

# w1 = wordnet.synset("corona.n.01")
# values = []
# for w in filtered_words:
#     try:
#         w2 = wordnet.synset(w + ".n.01")
#         values.append(w1.wup_similarity(w2))
#     except:
#         values.append(0)

# #print(values)

# m = max(values)
# indices = [i for i, j in enumerate(values) if j == m]
# print(indices)

# print(filtered_words[indices[0]])
# print(filtered_words[indices[1]])

# plt.plot(values)
# # plt.show()

# wordcloud = WordCloud(stopwords=stop_words).generate(text)

# plt.figure(figsize=(15,10))
# plt.clf()
# plt.imshow(wordcloud)
# plt.show()
