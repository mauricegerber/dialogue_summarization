import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

b1 = ["hi chris, our haiku johnson's nice to meet. you. nice to meet you kate.  chris. please tell me a little bit about yourself. i'm currently finishing my masters of education program at lake erie college and working on transitioning from a northeastern ohio inner to being a member of the jacksonville area community. why the move.  well, my wife's job is moving down south and i'm coming along with her.  it's very noble and my admirer beloved about you at the same time. how did you hear about the position open with our company here at rei? well, when i thought. about the opportunity of changing locations and moving from one physical location to another i thought about making a career move as well and i was starting with my main interests and passions and i love being outside. i love doing outdoor activities and i love working with people and i thought if i could use my experience as a teacher helping people and my interest in the outdoors together. it would be a good place to start a new career. and when i was looking online, i found re eyes website and that there were positions available in the jacksonville area. so i thought i would apply great.  well, you say you have an interest in outdoor activities. so this would be a great company for you to work at that being said what else do you know about our company?  well, i know you've been around for a long time since the late 1930s and what really caught my attention the most was the idea that it was started by people who had a passion for the outdoors. and found a way to involve others in their experience. i like the idea too that your company is consistently ranked among the top 100 companies to work for by fortune magazine, and i thought growing with a company that has that level of success would be a good place to be great.  why why do you want this particular position here with on within our customer service department?  because i want to start in a position that allows me to learn everything about the company from the very basic level of interacting with the customers all the way up throughout the sales process the marketing process and the production of goods and services when i saw the opportunity for customer service, i thought of the line very well with the skill set that i have and also with some skills that i could bring to the company that might be unique."]
b2 = ["you tell me a little bit more about these skills that you would transfer from your previous line of work to our department here.  sure in education. it's all about making the customer or student feel comfortable and helping them grow. i feel that within a company like rei. it's the same philosophy getting a customer comfortable with the product and helping them grow as they advance in whatever sport they happen to be participating in.  why do you think that our company should hire you specifically amongst our pool of candidates that are interviewing for this position.  sure, i think one skill set that i have involves my background in education teachers are among the highest stressed professionals in the workplace and rei offers a number of products that help alleviate stress by getting people outdoors and teachers also have a lot of downtime in the summers. my thinking is that once i learn the ropes and advance within the company, i'll be able to market the services and products that are i offers specifically to the teaching. profession great.  i have to ask this question given that you are making a career change here, especially with finishing a master's degree in education. if a position becomes available in your current field down here in the jacksonville area. how do you approach being offered this job versus being offered a position in your field and i'm asking that in the now and future.  sure. that's a great question. i'm not pursuing further educational opportunities within that profession. i feel like this customer service opportunity the chance to work in a field that i enjoy as much as teaching is a place that i could grow into long-term. so what i get out of teaching is working with people and helping people become a little bit better than they were when i first met them and that skill translates very well into our apis mission and so i don't anticipate leaving a successful career for something. i've already done. i feel like this is a natural confluence of my to interests."]
b3 = ["chris. what would you identify as your greatest professional strengths?  i think patients is probably my greatest strength that translates across the careers being able to listen to a student or customers difficulty and help them overcome that quality with patience and compassion is my greatest strength.  would you consider any weaknesses that you have to be detrimental to the job?  i think there's a risk when it comes to compassion. i think people can misinterpret compassion as being easy or willing to roll over when it's important to understand that compassion is something that is earned and it's interactive and i feel like if i establish clear boundaries he's with customers clients students. they understand that i am understanding. i am patient. i am kind yet. i'm also going to hold the people i interact with to a high standard.  to date. what would you say is your greatest professional achievement? personally becoming a teacher earning a master's degree. those have all been wonderful experiences for me. but the greatest achievement would have to be working with young people and helping them get a little bit better at communicating with the world around them.  chris can you tell me about a challenge or conflict that you faced in the workplace and how you would deal with it? sure."]
b4 = ["within the education profession. there are challenges every day. you're dealing with hundreds of different hundreds of different personalities and interests and levels of enthusiasm. so being able to engage students with content and enriching way is part of overcoming a conflict or difficulty. i think building professional relationships is another way to deal with conflicts understanding where people come from prior to teaching i was involved with a photography company photographing events, like weddings and bar mitzvahs and very very important events in people's lives and a lot of times conflicts that arise. so again, just like in teaching overcoming those conflicts with with patients and listening to the client or customers needs is very important.  now you are interviewing for a position that is not an entry level position and there is the possibility that those in our company that were overlooked for this position may have some animosity regarding the new hire for this position. so how do you approach this potential challenge here at the workplace?  the important thing is to listen to the people around me and understand that i am a newcomer and that they know more about the work environment then i will coming in. i think because i have a friendly demeanor and i'm not confrontational when meeting new people that in time will have a chance to earn each other's mutual respect and understand that we both want the same thing the company to grow and us to grow within the company.  where do you see yourself in five years, specifically he within our company.  hopefully i'll be able to develop a market that allows me to interact with people within the teaching profession and and grow our brand using that market as a target client base. it's great.  are you interviewing currently with any other companies and if so what interests you about those particular companies as well.  since i'm new to the area. i haven't had the opportunity to interview with a wide variety of companies. i have looked at bass pro shops and i'm currently scheduled to interview with them. they have a similar mission and similar goals to rei. it's just that their product line is more specifically tailored than re is more diverse offerings."]
b5 = ["we here at rei, you know, it is being in customer service. there are aspects of your job that are going to be a little less active than i could expect you being in a teaching position where i assume you're on your feet more one-on-one face-to-face with individuals. do you prefer a specific type of work environment? do you thrive in a variety of work environments? and what does this look like?  well, i thrive in variety of work environments i wouldn't expect to be sitting in a cubicle interacting with customers unless i'm handling a phone call and that's fine. that's part of the job. but what i would expect is to be actively engaged with the customers who come into the store and helping show them the products that might best suit their needs and introducing them to products that they might not have considered before. so what i've expected to be up moving around and being consistently engaged with a customer or trying to find ways to improve what we offer to our customers.  can you describe a time for me ever that you may have disagreed on a decision that was made for you and staff members at work. and how did you deal with this?  sure within the field of education. there are new initiatives being rolled out all the time. and sometimes those initiatives get mandated you have to teach this way this many times a week and when something like that happens, i think it's important to go back to what you know about your profession or your skill set and be able to provide research that supports why you do what you do. and i think when faced with a difficulty again, it's important to do what the boss says and it's an important to also advocate for what might be best for the customer or student.  all right, we're going to move on to some cognitive behavioral questions. and basically these questions are designed. they're not necessarily about your past your experience. there are sort of out of the box."]
b6 = ["questions. and. so just do your best at answering them as her go through this. so if you were an animal, what would you be and why?  tough question, i think. considering the the traits of my dog if i had to be an animal i would certainly want to be a domesticated dog. they just have that ability to love unconditionally, they're intensely loyal and they just provide so many benefits to people something. i'd like to do in my life as a human to great. the next question how many tennis balls can you fit into a limousine.  tennis balls in the limousine? i guess to effectively answer that question. i would need some help. i would need to know what type of limousine because if we're talking about a stretch suv. that's a much larger volume than a smaller limousine. are we talking to door for door? i also don't know what's in the limousine already other people in there or is it empty once i had those questions answered i'd have to do some calculations about the size of a tennis ball how much area or how much volume it takes up calculate the inside of the limousine and then and make sure the math works out i could get that answer to you. i just can't do it off the top of my head, right?  let me ask this final question are do you have any questions for us?  well, i mentioned a couple times about being interested in helping grow a market for rei. i'm just curious as a new employee or someone starting out on the lower level. how open is upper management hearing the ideas of an employee.  we do try to have monthly meetings where we meet with a variety of employees at random. so these aren't things that are necessarily scheduled regularly, they're very they're very semiannual. they're very informal. we do like to hear our employees opinions about our products, especially and about marketing. one thing that we don't necessarily do is the lower level positions that are dealing maybe with collections or you know, the intake and distribution of customer service calls. we don't necessarily talk to that group of employees. he's very often but i'd be very interested to hear your opinions on that. should you be hired for the position and maybe ways that we could do better as well by reaching a larger group of our employees to benefit our company."]

b_all = b1+b2+b3+b4+b5+b6

vectorizer = TfidfVectorizer()
vectors = vectorizer.fit_transform([b1[0], b2[0], b3[0], b4[0], b5[0], b6[0]])
feature_names = vectorizer.get_feature_names()
dense = vectors.todense()
denselist = dense.tolist()
df = pd.DataFrame(denselist, columns=feature_names)

# pd.set_option("display.max_rows", None, "display.max_columns", None)
# print(df)

# for i in range(len(df.columns)):
#     for j in range(len(df)):
#         if df.iloc[j][i] > 0.2:
#             print(df.columns[i], df.iloc[j][i])

###################################################################
# self implemented
import string
adj_punctuation = string.punctuation.replace("'", "")

import re

from nltk.corpus import stopwords
stopwords = stopwords.words('english')
stopwords.append(["i'll", "don't", "i've", "i'd", "i'm", "can't", "we're", "what's", "that's", "there's", "they're"])


# Remove punctuation and create list of words
bagOfWordsA = b1[0].translate(str.maketrans('', '', adj_punctuation)).split(' ')
bagOfWordsB = b2[0].translate(str.maketrans('', '', adj_punctuation)).split(' ')
bagOfWordsC = b3[0].translate(str.maketrans('', '', adj_punctuation)).split(' ')
bagOfWordsD = b4[0].translate(str.maketrans('', '', adj_punctuation)).split(' ')
bagOfWordsE = b5[0].translate(str.maketrans('', '', adj_punctuation)).split(' ')
bagOfWordsF = b6[0].translate(str.maketrans('', '', adj_punctuation)).split(' ')

uniqueWords = set(bagOfWordsA).union(set(bagOfWordsB), set(bagOfWordsC), set(bagOfWordsD), set(bagOfWordsE), set(bagOfWordsF))

numOfWordsA = dict.fromkeys(uniqueWords, 0)
for word in bagOfWordsA:
    numOfWordsA[word] += 1
numOfWordsB = dict.fromkeys(uniqueWords, 0)
for word in bagOfWordsB:
    numOfWordsB[word] += 1
numOfWordsC = dict.fromkeys(uniqueWords, 0)
for word in bagOfWordsC:
    numOfWordsC[word] += 1
numOfWordsD = dict.fromkeys(uniqueWords, 0)
for word in bagOfWordsD:
    numOfWordsD[word] += 1
numOfWordsE = dict.fromkeys(uniqueWords, 0)
for word in bagOfWordsE:
    numOfWordsE[word] += 1
numOfWordsF = dict.fromkeys(uniqueWords, 0)
for word in bagOfWordsF:
    numOfWordsF[word] += 1





def computeTF(wordDict, bagOfWords):
    tfDict = {}
    bagOfWordsCount = len(bagOfWords)
    for word, count in wordDict.items():
        tfDict[word] = count / float(bagOfWordsCount)
    return tfDict

# Frequency in Block
tfA = computeTF(numOfWordsA, bagOfWordsA)
tfB = computeTF(numOfWordsB, bagOfWordsB)
tfC = computeTF(numOfWordsC, bagOfWordsC)
tfD = computeTF(numOfWordsD, bagOfWordsD)
tfE = computeTF(numOfWordsE, bagOfWordsE)
tfF = computeTF(numOfWordsF, bagOfWordsF)

# log(Frequency in Document)
def computeIDF(documents):
    import math
    N = len(documents)
    
    idfDict = dict.fromkeys(documents[0].keys(), 0)
    for document in documents:
        for word, val in document.items():
            if val > 0:
                idfDict[word] += 1
    
    for word, val in idfDict.items():
        idfDict[word] = math.log(N / float(val))
    return idfDict

idfs = computeIDF([numOfWordsA, numOfWordsB, numOfWordsC, numOfWordsD, numOfWordsE, numOfWordsF])

# Frequency in Block * log(Frequency in Document)
def computeTFIDF(tfBagOfWords, idfs):
    tfidf = {}
    for word, val in tfBagOfWords.items():
        tfidf[word] = val * idfs[word]
    return tfidf

tfidfA = computeTFIDF(tfA, idfs)
tfidfB = computeTFIDF(tfB, idfs)
tfidfC = computeTFIDF(tfC, idfs)
tfidfD = computeTFIDF(tfD, idfs)
tfidfE = computeTFIDF(tfE, idfs)
tfidfF = computeTFIDF(tfF, idfs)



df = pd.DataFrame([tfidfA, tfidfB, tfidfC, tfidfD, tfidfE, tfidfF])

for i in range(len(df.columns)):
    for j in range(len(df)):
        if df.iloc[j][i] > 0.015:
            print(df.columns[i], df.iloc[j][i])

pd.set_option("display.max_rows", None, "display.max_columns", None)
#print(df)