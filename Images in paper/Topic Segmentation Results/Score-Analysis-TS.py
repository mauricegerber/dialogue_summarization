import numpy as np


def convert_to_seconds(t):
    return int(t[:2])*60 + int(t[3:])


def analyze_distance(timestamps1, timestamps2):
    smallest_values = []
    for t1 in timestamps1[1:-1]:
        diff = list(map(lambda t2: abs(t1 - t2), timestamps2[1:-1]))
        smallest_values.append(min(diff)/timestamps1[-1]*100/np.sqrt(len(timestamps1[1:-1])))
    
    return smallest_values
    
def segmentation_score(timestamp1, timestamp2):
    timestamp1_s = [convert_to_seconds(t) for t in timestamp1]
    timestamp2_s = [convert_to_seconds(t) for t in timestamp2]

    d1 = analyze_distance(timestamp1_s, timestamp2_s) 
    d2 = analyze_distance(timestamp2_s, timestamp1_s)
    print(d1, d2)
    return round(np.mean(d1+d2),2)


test1 = ["00:00", "29:34", "45:29", "46:08", "47:12"]
test2 = ["00:00", "19:34", "34:39", "45:08", "47:12"]

test1 = ["00:00", "22:38", "29:34", "45:29", "47:12"]
test2 = ["00:00", "19:34", "34:39", "45:08", "47:12"]

test1 = ["00:00", "20:34", "35:29", "46:08", "47:12"]
test2 = ["00:00", "19:34", "34:39", "45:08", "47:12"]

test1 = ["00:00", "01:01", "07:12"]
test2 = ["00:00", "06:11", "07:12"]

# test1 = ["00:00", "19:34", "34:39", "41:44", "45:08", "47:12"]
# test2 = ["00:00", "13:40", "24:52", "26:57", "41:44", "47:12"]

# test1 = ["00:00", "05:34", "09:39", "11:44", "14:08"]
# test2 = ["00:00", "03:40", "08:52", "11:57", "14:08"]

segscore = segmentation_score(test1,test2)
print(segscore)