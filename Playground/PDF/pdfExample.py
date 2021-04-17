import pathlib
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

source = str(pathlib.Path(__file__).parent.absolute())

## Data
transcript = pd.read_csv(
    filepath_or_buffer= source + "\Vice presidential debate.csv",
    header=0,
    names=["Speaker", "Time", "End time", "Duration", "Utterance"],
    usecols=["Speaker", "Time", "Utterance"],
)
transcript["Time"] = transcript["Time"].str.replace("60", "59")
t_short = transcript[0:5]



## Main
fileName = source + '\MyDoc.pdf'
# documentTitle = 'Test'
title = 'Dialog Analyzer'
subTitle = 'created 17.04.2021'

## Fonts
# # Print available fonts
# for font in pdf.getAvailableFonts():
#     print(font)
# Register a new font
font_s = source + '/Nunito_Sans/NunitoSans-Regular.ttf'

pdfmetrics.registerFont(
    TTFont('Nunito_Sans', font_s)
)

# ###################################
# Help
def drawMyRuler(pdf):
    pdf.drawString(100,810, 'x100')
    pdf.drawString(200,810, 'x200')
    pdf.drawString(300,810, 'x300')
    pdf.drawString(400,810, 'x400')
    pdf.drawString(500,810, 'x500')

    pdf.drawString(10,100, 'y100')
    pdf.drawString(10,200, 'y200')
    pdf.drawString(10,300, 'y300')
    pdf.drawString(10,400, 'y400')
    pdf.drawString(10,500, 'y500')
    pdf.drawString(10,600, 'y600')
    pdf.drawString(10,700, 'y700')
    pdf.drawString(10,800, 'y800')    

# ###################################
# Content
textLines = [
'The Tasmanian devil (Sarcophilus harrisii) is',
'a carnivorous marsupial of the family',
'Dasyuridae.']

# ###################################
# Create document 
pdf = canvas.Canvas(fileName)
# pdf.setTitle(documentTitle)
pdf.setFont('Nunito_Sans', 6)
drawMyRuler(pdf)


# ###################################
# Title
pdf.setFont('Nunito_Sans', 24)
pdf.drawCentredString(300, 770, title)

# Sub Title 
pdf.setFont('Nunito_Sans', 12)
pdf.drawCentredString(290,720, subTitle)


## Table
elements = []
data= [['00', '01', '02', '03', '04'],
['10', '11', '12', '13', '14'],
['20', '21', '22', '23', '24'],
['30', '31', '32', '33', '34']]
t=Table(data)

elements.append(t)

pdf.(elements)





pdf.save()










# #########################################################################################################
# 3) Draw a line
# pdf.line(30, 710, 550, 710)

# ###################################
# 4) Text object :: for large amounts of text
# text = pdf.beginText(40, 680)
# for line in textLines:
#     text.textLine(line)
# pdf.drawText(text)

# 5) Draw a image
# image = source + '/tasmanianDevil.jpg'
# pdf.drawInlineImage(image, 130, 400)