thisdict = {
  "brand": [0,0,0,0,0],
  "model": [1,2,3,4,5],
  "year": [0,0,0,0,0]
}

print(thisdict)

thisdict["brand"][0] += 1

for key, value in thisdict.items():
  print(key, value)

print(thisdict)