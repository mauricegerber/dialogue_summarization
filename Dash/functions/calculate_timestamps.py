import math
from datetime import datetime

def calculate_timestamps(transcript):
    first_timestamp = datetime.strptime("00:00:00", "%H:%M:%S")
    timestamps_hms = []
    timestamps_s = []
    # time column has format %M:%S and minutes can exceed 59
    # e.g. time value of 65:46 corresponds to 01:05:46 in %H:%M:%S format
    for time in transcript["Time"]:
        time = time.split(":")
        h = math.floor(int(time[0]) / 60)
        m = int(time[0]) % 60
        s = time[1]
        if s == "60": s = "59" # seconds can have value of 60 which would be non-convertible
        hms = ":".join([str(h), str(m), s])
        current_timestamp = datetime.strptime(hms, "%H:%M:%S")
        if current_timestamp.hour == 0:
            timestamps_hms.append("{:02d}:{:02d}".format(current_timestamp.minute,
                                                         current_timestamp.second))
        else:
            timestamps_hms.append("{:02d}:{:02d}:{:02d}".format(current_timestamp.hour,
                                                                current_timestamp.minute,
                                                                current_timestamp.second))
        timestamps_s.append(int((current_timestamp - first_timestamp).total_seconds()))
    transcript["Time"] = timestamps_hms
    transcript["Timestamp"] = timestamps_s