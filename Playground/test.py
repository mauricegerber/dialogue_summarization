from datetime import datetime
import math


first_timestamp = datetime.strptime("0:00", "%M:%S")

second_timestamp = "10:49"

third_timestamp = "63:46"

#diff = int((second_timestamp - first_timestamp).total_seconds())

#print(diff)

s = third_timestamp.split(":")
s2 = "63:46".split(":")

print(s2)

h = math.floor(int(s2[0]) / 60)
m = int(s2[0]) % 60
sec = s2[1]

print(h)
print(m)
print(s2[1])

f = ":".join([str(h),str(m),str(sec)])

print(f)

d = datetime.strptime(f, "%H:%M:%S")

print(strd.hour + "asdf")

print("{:d}:{:02d}:{:02d}".format(d.hour, d.minute, d.second))


