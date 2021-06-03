import sys
import os

import string

sys.path.insert(0, os.path.split(sys.path[0])[0])
path = sys.path[0]

# punctuation
f1 = open(path + "/Stopwords/punctuation_formatted.txt", "x")
f1.write(" ".join(string.punctuation))
f1.close()

# # yake_german
# f1 = open(path + "/Stopwords/yake_german.txt", "r")
# stopwords = []
# for line in f1:
#     stopwords.append(line.strip("\n"))

# # print(stopwords)

# f2 = open(path + "/Stopwords/yake_german_formatted.txt", "x")
# f2.write(", ".join(stopwords))
# f2.close()

# # yake_english
# f1 = open(path + "/Stopwords/yake_english.txt", "r")
# stopwords = []
# for line in f1:
#     stopwords.append(line.strip("\n"))

# # print(stopwords)

# f2 = open(path + "/Stopwords/yake_english_formatted.txt", "x")
# f2.write(", ".join(stopwords))
# f2.close()

# # nltk_german
# f1 = open(path + "/Stopwords/nltk_german", "r")
# stopwords = []
# for line in f1:
#     stopwords.append(line.strip("\n"))

# # print(stopwords)

# f2 = open(path + "/Stopwords/nltk_german_formatted.txt", "x")
# f2.write(", ".join(stopwords))
# f2.close()

# # nltk_english
# f1 = open(path + "/Stopwords/nltk_english", "r")
# stopwords = []
# for line in f1:
#     stopwords.append(line.strip("\n"))

# # print(stopwords)

# f2 = open(path + "/Stopwords/nltk_english_formatted.txt", "x")
# f2.write(", ".join(stopwords))
# f2.close()
