def split_dialog(data, steps=5):
    nrow = len(data)-1
    last_min = data[nrow]["Time"]
    l_min = int(last_min[0:2])

    minutes = range(0, l_min+steps, steps)
    minutes = minutes[1:]
    
    def analyse_minute(timestamp):
        minute = 0
        if len(timestamp) > steps:
            minute = 60 * int(timestamp[0:timestamp.find(":",0,len(timestamp))])
            timestamp = timestamp[timestamp.find(":",0,len(timestamp))+1:]
            
        minute += int(timestamp[0:timestamp.find(":",0,len(timestamp))])
        return(minute)
    
    text = ""
    text_old = ""
    index_min = 0
    text_data = []
    
    for i in range(nrow+1):
        t = data[i]["Utterance"]
        min_count = analyse_minute(data[i]["Time"])

        if min_count < minutes[index_min]:
            text += " " + t
            
        else:
            text_data.append([text])
            index_min += 1
            text = data[i]["Utterance"]

        if i == nrow:
            text_data.append([text])
   
    return text_data