from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import pandas as pd
import numpy as np
from datetime import datetime

def create_pdf(transcript):
    # Font
    font_s = './functions/Nunito_Sans/NunitoSans-Regular.ttf'
    pdfmetrics.registerFont(
        TTFont('Nunito_Sans', font_s)
    )

    # Styles
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

    def insert_linebreak(text_column):
        new_column = []
        for u in text_column:
            for i in range(len(u)):
                if i % 100 == 0:
                    u = u[:i] + "\n" + u[i:]
            new_column.append(u)
        return new_column
    
    ##################################################
    transcript["Utterance"] = insert_linebreak(transcript["Utterance"])
    data = transcript.values
    
    now = datetime.now()
    current_time = now.strftime("%H_%M_%S")

    file_name = "./downloadable/test" + current_time + ".pdf"
    doc = SimpleDocTemplate(file_name, pagesize=letter)

    elements = []
    elements.append(Paragraph("Dialog Analyzer", TitleStyle))
    elements.append(Paragraph("PDF created 17.04.2021", SubtitleStyle))
    
    data = data.tolist()
    t=Table(data)
    elements.append(t)
    
    doc.build(elements)
    return file_name

