import nltk
from reportlab.pdfgen import canvas
import pandas as pd
import numpy as np
import ast
import cairo

transcript = pd.read_csv(
    filepath_or_buffer="Playground\Vice presidential debate.csv",
    header=0,
    names=["Speaker", "Time", "End time", "Duration", "Utterance"],
    usecols=["Speaker", "Time", "Utterance"],
)
transcript["Time"] = transcript["Time"].str.replace("60", "59")
t_short = transcript[1:5]

c = canvas.Canvas("test.pdf")
c.drawString(100,100,transcript[["Speaker"]])
c.showPage()
c.save()


# d = {"name": ["p1","p2","p1"], "text":["hello everybody","hello, how are you doing?","Great."]}
# df = pd.DataFrame(d)

# c = canvas.Canvas("test.pdf")
# c.drawString(100,100,df[["name"]].decode("uft8"))
# c.showPage()
# c.save()

# print(df[["name"]])
#############################################################################
# df = t_short
# HTML_TEMPLATE1 = '''
#     <html>
#     <head>
#     <style>
#     h2 {
#         text-align: center;
#         font-family: Helvetica, Arial, sans-serif;
#     }
#     table { 
#         margin-left: auto;
#         margin-right: auto;
#     }
#     table, th, td {
#         border: 1px solid black;
#         border-collapse: collapse;
#     }
#     th, td {
#         padding: 5px;
#         text-align: center;
#         font-family: Helvetica, Arial, sans-serif;
#         font-size: 90%;
#     }
#     table tbody tr:hover {
#         background-color: #dddddd;
#     }
#     .wide {
#         width: 90%; 
#     }
#     </style>
#     </head>
#     <body>
# '''

# HTML_TEMPLATE2 = '''
# </body>
# </html>
# '''


# def to_html_pretty(df, filename='/tmp/out.html', title=''):
#     '''
#     Write an entire dataframe to an HTML file
#     with nice formatting.
#     Thanks to @stackoverflowuser2010 for the
#     pretty printer see https://stackoverflow.com/a/47723330/362951
#     '''
#     ht = ''
#     if title != '':
#         ht += '<h2> %s </h2>\n' % title
#     ht += df.to_html(classes='wide', escape=False)

#     with open(filename, 'w') as f:
#          f.write(HTML_TEMPLATE1 + ht + HTML_TEMPLATE2)




# # Pretty print the dataframe as an html table to a file
# intermediate_html = 'intermediate.html'
# to_html_pretty(df,intermediate_html,'PDF Output')
# # if you do not want pretty printing, just use pandas:
# #df.to_html(intermediate_html)

# # Convert the html file to a pdf file using weasyprint
# import weasyprint
# out_pdf= 'demo.pdf'
# weasyprint.HTML(intermediate_html).write_pdf(out_pdf)

# # This is the table pretty printer used above:

