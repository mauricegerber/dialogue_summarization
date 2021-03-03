import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk
import string

df = pd.read_csv("./Data/us_election_2020_1st_presidential_debate.csv")
df = df[:100]
df["filtered text"] = ""
df["most common words"] = ""

stop_words = set(stopwords.words("english") + list(string.punctuation) + ["’"])
#print(stop_words)

separator = " "
for i in range(len(df)):
    text = df["text"][i].lower()
    words = word_tokenize(text)
    filtered_words = []
    for w in words:
        if w not in stop_words:
            filtered_words.append(w)

    word_dist = nltk.FreqDist(filtered_words)
    most_common = ""
    for word, frequency in word_dist.most_common(3):
        most_common += word + " "
    df["filtered text"][i] = separator.join(filtered_words)
    df["most common words"][i] = most_common

html = df.to_html()

# Save pandas dataFrame as html table
text_file = open("index.html", "w")
text_file.write(html)
text_file.close()
