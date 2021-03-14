from datetime import datetime



now = datetime.strptime("0:00", "%M:%S")

later = datetime.strptime("8:00", "%M:%S")


difference = (later - now).total_seconds()




print(difference)