from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import pathlib
import pandas as pd
import numpy as np

source = str(pathlib.Path(__file__).parent.absolute())

def insert_linebreak(data):
    new_data = []
    for u in data:
        for i in range(len(u)):
            if i % 100 == 0:
                u = u[:i] + "\n" + u[i:]
        new_data.append(u)
    return new_data
      

## Data
transcript = pd.read_csv(
    filepath_or_buffer= source + "\Vice presidential debate.csv",
    header=0,
    names=["Speaker", "Time", "End time", "Duration", "Utterance"],
    usecols=["Speaker", "Time", "Utterance"],
)
transcript["Time"] = transcript["Time"].str.replace("60", "59")
t_short = transcript[0:10]
t_short["Utterance"] = insert_linebreak(t_short["Utterance"])

data = t_short.values


# Add new Font
font_s = source + '/Nunito_Sans/NunitoSans-Regular.ttf'
pdfmetrics.registerFont(
    TTFont('Nunito_Sans', font_s)
)

# container for the 'Flowable' objects
style = getSampleStyleSheet()

TitleStyle = ParagraphStyle('yourtitle',
                           fontName="Nunito_Sans",
                           fontSize=16,
                           alignment=1,
                           spaceAfter=14)

SubtitleStyle = ParagraphStyle('yourtitle',
                           fontName="Nunito_Sans",
                           fontSize=11,
                           alignment=1,
                           spaceAfter=14)

TextStyle = ParagraphStyle('yourtitle',
                           fontName="Nunito_Sans",
                           fontSize=10,
                           alignment=1,
                           spaceAfter=14)

doc = SimpleDocTemplate(source + "/test.pdf", pagesize=letter)

elements = []

elements.append(Paragraph("This is a Heading", TitleStyle))
elements.append(Paragraph("This is a paragraph in <i>Normal</i> style. 3210", SubtitleStyle))


data = data.tolist()
# data= [['00', '01', '02', '03', '04'],
# ['10', '11', '12', '13', '14'],
# ['20', '21', '22', '23', '24'],
# ['30', '31', '32', '33', '34']]
t=Table(data)

elements.append(t)
# write the document to disk
doc.build(elements)

