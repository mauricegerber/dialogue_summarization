import os
import pandas as pd
import numpy as np
from datetime import datetime
import time
import base64
import io
import re
import math

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import dash_table

import plotly.express as px
import plotly.graph_objects as go

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

from nltk.tokenize.api import TokenizerI

ps = PorterStemmer()


from summa import keywords
# from pytopicrank import TopicRank

BS = "https://stackpath.bootstrapcdn.com/bootswatch/4.5.2/lux/bootstrap.min.css"
app = dash.Dash(external_stylesheets=[BS])

def calculate_timestamps(transcript):
    first_timestamp = datetime.strptime("0:00", "%M:%S")
    timestamps = []
    for t in transcript["Time"]:
        if len(t) <= 5:
            current_timestamp = datetime.strptime(t, "%M:%S")
            timestamps.append(int((current_timestamp - first_timestamp).total_seconds()))
        else:
            current_timestamp = datetime.strptime(t, "%H:%M:%S")
            timestamps.append(int((current_timestamp - first_timestamp).total_seconds()))
    transcript["Timestamp"] = timestamps

transcripts_dir = "./transcripts/"
transcripts_files = os.listdir(transcripts_dir)
initial_transcript_index = 1

transcripts = []
for file in transcripts_files:
    transcript = pd.read_csv(
        filepath_or_buffer=transcripts_dir + file,
        header=0,
        names=["Speaker", "Time", "End time", "Duration", "Utterance"],
        usecols=["Speaker", "Time", "Utterance"]
    )
    transcript["Time"] = transcript["Time"].str.replace("60", "59")
    calculate_timestamps(transcript)
    transcripts.append(transcript)

initial_transcript = transcripts[initial_transcript_index]
initial_timeline_min = initial_transcript["Timestamp"][0]
initial_timeline_max = initial_transcript["Timestamp"][initial_transcript.index[-1]]

app.layout = dbc.Container(
    [
        html.Br(),
        html.H1("Dialog analyzer"),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Select(
                            id="transcript_selector",
                            options=[{"label": transcripts_files[i], "value": i} for i in range(len(transcripts_files))],
                            value=initial_transcript_index,
                        ),
                    ],
                    width=3,
                ),
                dbc.Col(
                    [
                        dcc.Upload(children = [dbc.Button("Upload", style={"width": "100%"})], id = "upload_input", style={"width": "8%"}),
                        html.Div(id="output-data-upload", children = []),

                        dbc.Modal([
                            dbc.ModalHeader("Upload succesfull"),
                            dbc.ModalBody(html.Div(id = "output_file")),
                            dbc.ModalFooter(
                                dbc.Button("Close", id="close", className="ml-auto")
                                ),
                            ],
                            id="modal_upload",
                        ),
                    ],
                ),
            ],
        ),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Tabs(
                            [
                                dbc.Tab(label="Transcript", id="transcript_tab", children=[
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    html.Br(),
                                                    html.H5("Select speaker"),
                                                    dbc.Checklist(
                                                        id="speaker_selector",
                                                        options=[{"label": i, "value": i}
                                                                 for i in sorted(initial_transcript["Speaker"].unique(),
                                                                 key=str.lower)],
                                                        value=initial_transcript["Speaker"].unique(),
                                                    ),
                                                ],
                                                width=2,
                                            ),
                                            dbc.Col(
                                                [
                                                    html.Br(),
                                                    html.H5("Select time"),
                                                    dbc.Row(
                                                        [
                                                            dbc.Col(
                                                                [
                                                                    dbc.Input(
                                                                        id="start_time_input",
                                                                        type="time",
                                                                        value="00:00",
                                                                    ),
                                                                ],
                                                                width="100px",
                                                            ),
                                                            dbc.Col(
                                                                [
                                                                    dcc.RangeSlider(
                                                                        id="timeline_slider",
                                                                        min=initial_timeline_min,
                                                                        max=initial_timeline_max,
                                                                        value=[initial_timeline_min, initial_timeline_max],
                                                                        marks={},
                                                                    ),
                                                                ],
                                                                width=9,
                                                            ),
                                                            dbc.Col(
                                                                [
                                                                    dbc.Input(
                                                                        id="end_time_input",
                                                                        type="time",
                                                                        value=time.strftime("%H:%M",
                                                                                            time.gmtime(initial_timeline_max)),
                                                                    ),
                                                                ],
                                                                width="100px",
                                                            ),
                                                        ],
                                                    ),  
                                                ],
                                                width=8,
                                            ),
                                            dbc.Col(
                                                [
                                                    html.Br(),
                                                    html.H5("Search"),
                                                    dbc.Input(
                                                        id="search_input",
                                                        type="search",
                                                        placeholder="Enter search term here",
                                                    ),
                                                ],
                                                width=2,
                                            ),
                                        ],
                                    ),
                                    html.Br(),
                                    dash_table.DataTable(
                                        id="transcript_table",
                                        columns=[
                                            {"name": "Speaker", "id": "Speaker", "presentation": "markdown"},
                                            {"name": "Time", "id": "Time", "presentation": "markdown"},
                                            {"name": "Utterance", "id": "Utterance", "presentation": "markdown"}
                                        ],
                                        data=initial_transcript[["Speaker", "Time", "Utterance"]].to_dict("records"),
                                        style_data_conditional=[
                                            {"if": {"state": "selected"},
                                             "background-color": "white",
                                             "border": "1px solid rgba(0,0,0,0.05)"},
                                        ],
                                        style_header={
                                            "font-size": "0.9rem",
                                            "background-color": "#f7f7f9",
                                            "border": "1px solid rgba(0,0,0,0.05)",
                                        },
                                        style_cell_conditional=[
                                            {"if": {"column_id": "Speaker"},
                                             "width": "150px"},
                                            {"if": {"column_id": "Time"},
                                             "width": "100px"},
                                            {"if": {"column_id": "Utterance"},
                                             "width": "1450px"},
                                        ],
                                        style_cell={
                                            "white-space": "normal",
                                            "padding": "1.5rem",
                                            "border": "1px solid rgba(0,0,0,0.05)",   
                                        },
                                        fixed_rows={"headers": True},
                                        page_action="none",
                                    ),
                                ],
                                ),
                                dbc.Tab(label="Keywords", id="keywords_tab", children=[
                                    dcc.Graph(id="keywords_plot", figure={}),
                                    dcc.Graph(id="keywords_plot2", figure={}),
                                ],
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ],
    fluid=True,
)

@app.callback(
    Output(component_id="transcript_table", component_property="data"),
    Output(component_id="speaker_selector", component_property="options"),
    Output(component_id="speaker_selector", component_property="value"),
    Output(component_id="start_time_input", component_property="value"),
    Output(component_id="end_time_input", component_property="value"),
    Output(component_id="timeline_slider", component_property="min"),
    Output(component_id="timeline_slider", component_property="max"),
    Output(component_id="timeline_slider", component_property="value"),
    Output(component_id="timeline_slider", component_property="marks"),
    Output(component_id="search_input", component_property="value"),
    Input(component_id="transcript_selector", component_property="value"),
    Input(component_id="speaker_selector", component_property="value"),
    Input(component_id="start_time_input", component_property="value"),
    Input(component_id="end_time_input", component_property="value"),
    Input(component_id="timeline_slider", component_property="value"),
    Input(component_id="search_input", component_property="value"),
)
def update_transcript_table_and_filters(selected_transcript, selected_speaker, selected_start_time,
                                        selected_end_time, selected_timeline, search_term):
    transcript = transcripts[int(selected_transcript)]

    timeline_min = transcript["Timestamp"][0]
    timeline_max = transcript["Timestamp"][transcript.index[-1]]
    timeline_deviation = timeline_max - int(timeline_max/60)*60

    trigger = dash.callback_context.triggered[0]["prop_id"]

    if trigger == "transcript_selector.value":
        speakers = transcript["Speaker"].unique()
        transcript_table = transcript[["Speaker", "Time", "Utterance"]].to_dict("records")
        
        return (transcript_table, [{"label": i, "value": i} for i in sorted(speakers, key=str.lower)], speakers,
                "00:00", time.strftime("%H:%M", time.gmtime(timeline_max)),
                timeline_min, timeline_max, [timeline_min, timeline_max], dict(), None)
    
    if trigger != "." and trigger != "transcript_selector.value":
        marks = dict()
        transcript = transcript[transcript["Speaker"].isin(selected_speaker)]
        
        if search_term != None and len(search_term) > 1:
            transcript = transcript[transcript["Utterance"].str.contains(search_term, case=False, regex=False)]
            if search_term[-1] == " ":
                transcript["Utterance"] = transcript["Utterance"].str.replace(search_term[:-1], "**" + search_term[:-1] + "**", case=False)
            else:
                transcript["Utterance"] = transcript["Utterance"].str.replace(search_term, "**" + search_term + "**", case=False)
            mark_symbol = ["|"] * len(transcript)
            marks = dict(zip(transcript["Timestamp"], mark_symbol))

        if trigger == "start_time_input.value" or trigger == "end_time_input.value":
            first_timestamp = datetime.strptime("0:00", "%M:%S")
            current_start_time = datetime.strptime(selected_start_time, "%H:%M")
            current_end_time = datetime.strptime(selected_end_time, "%H:%M")
            timeline_slider_values = [(current_start_time - first_timestamp).total_seconds(),
                                      (current_end_time - first_timestamp).total_seconds() + timeline_deviation]
            transcript = transcript[transcript["Timestamp"] >= timeline_slider_values[0]]
            transcript = transcript[transcript["Timestamp"] <= timeline_slider_values[1]]
            transcript_table = transcript[["Speaker", "Time", "Utterance"]].to_dict("records")
            
            return (transcript_table, dash.no_update, dash.no_update, dash.no_update, dash.no_update,
                    dash.no_update, dash.no_update, timeline_slider_values, marks, dash.no_update)

        transcript = transcript[transcript["Timestamp"] >= selected_timeline[0]]
        transcript = transcript[transcript["Timestamp"] <= selected_timeline[1]]
        transcript_table = transcript[["Speaker", "Time", "Utterance"]].to_dict("records")

        return (transcript_table, dash.no_update, dash.no_update,
                time.strftime("%H:%M", time.gmtime(selected_timeline[0])),
                time.strftime("%H:%M", time.gmtime(selected_timeline[1])),
                dash.no_update, dash.no_update, dash.no_update, marks, dash.no_update)

    return (dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update,
            dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update)

@app.callback(
    Output(component_id="keywords_plot", component_property="figure"),
    Output(component_id="keywords_plot2", component_property="figure"),
    Input(component_id="transcript_selector", component_property="value"),
)
def create_keywords_plot(selected_transcript):
    transcript = transcripts[int(selected_transcript)]

    text = ""
    counter = 0
    for t in transcript["Utterance"]:
        counter += 1
        text += " " + t
        if counter == 10:
            text += " " + t + "\n\n"
            counter = 0

    def _mark_paragraph_breaks(text):
        "Identifies indented text or line breaks as the beginning of paragraphs"
        MIN_PARAGRAPH = 100 # min number of characters for paragraph
        pattern = re.compile("[ \t\r\f\v]*\n[ \t\r\f\v]*\n[ \t\r\f\v]*") # https://regex101.com/
        matches = pattern.finditer(text) # gets positions of line breaks in text
        last_break = 0
        pbreaks = [0]
        for pb in matches:
            if pb.start() - last_break < MIN_PARAGRAPH: # if next line break within MIN_PARAGRAPH, skip it
                continue
            else:
                pbreaks.append(pb.start())
                last_break = pb.start()
        return pbreaks # return list of line break positions in text

    def _divide_to_tokensequences(text):
        "Divides the text into pseudosentences of fixed size"
        wrdindex_list = []
        matches = re.finditer("\w+", text) # gets positions of every word in text
        for match in matches:
            wrdindex_list.append((ps.stem(match.group()), match.start())) # list of tuples with word and word starting position
        return [TokenSequence(i / w, wrdindex_list[i : i + w]) for i in range(0, len(wrdindex_list), w)] # make an object of class TokenSequence
        # [(0.0, [('i', 1), ('m', 3), ('susan', 5), ('page', 11), ('of', 16), ('usa', 19), ('today', 23), ('it', 29), ('is', 32), ('my', 35), ('honor', 38), ('to', 44), ('moderate', 47), ('this', 56), ('debate', 61), ('an', 68), ('important', 71), ('part', 81), ('of', 86), ('our', 89)]),
        #  (1.0, [('democracy', 93), ('in', 103), ('kingsbury', 106), ('hall', 116), ('tonight', 121), ('we', 129), ('have', 132), ('a', 137), ('small', 139), ('and', 145), ('socially', 149), ('distant', 158), ('audience', 166), ('and', 175), ('we', 179), ('ve', 182), ('taken', 185), ('extra', 191), ('precautions', 197), ('during', 209)])]

    def _create_token_table(token_sequences, par_breaks):
        "Creates a table of TokenTableFields"
        token_table = {}
        current_par = 0
        current_tok_seq = 0
        pb_iter = par_breaks.__iter__()
        current_par_break = next(pb_iter) # iterator currently set to index 0

        if current_par_break == 0:
            try:
                current_par_break = next(pb_iter) # iterator increased to index 1
            except StopIteration:
                raise ValueError("No paragraph breaks were found(text too short perhaps?)")
                # if the text has no paragraphs, this error raised
        
        for ts in token_sequences:
            for word, index in ts.wrdindex_list:
                try:
                    while index > current_par_break:
                        current_par_break = next(pb_iter)
                        current_par += 1
                except StopIteration:
                    # hit bottom, no more paragraphs
                    pass

                if word in token_table: # check if word already appeared
                    # print("existing word: ", word)
                    token_table[word].total_count += 1

                    if token_table[word].last_par != current_par:
                        token_table[word].last_par = current_par
                        token_table[word].par_count += 1

                    if token_table[word].last_tok_seq != current_tok_seq:
                        token_table[word].last_tok_seq = current_tok_seq
                        token_table[word].ts_occurences.append([current_tok_seq, 1])
                    else:
                        token_table[word].ts_occurences[-1][1] += 1

                else: # create new word if it did not appear yet
                    token_table[word] = TokenTableField(
                        first_pos=index,
                        ts_occurences=[[current_tok_seq, 1]],
                        total_count=1,
                        par_count=1,
                        last_par=current_par,
                        last_tok_seq=current_tok_seq,
                    )
                    # print("new word: ", word)

            current_tok_seq += 1

        return token_table

    def _block_comparison(tokseqs, token_table):
            """Implements the block comparison method"""
            def blk_frq(tok, block):
                # print("tok ", tok)
                # print("block ", block)
                # print(token_table[tok].ts_occurences)
                ts_occs = filter(lambda o: o[0] in block, token_table[tok].ts_occurences) # checks if word occurs in the current block
                freq = sum([tsocc[1] for tsocc in ts_occs]) # sum of occurences in the current block
                # print("freq ", freq)
                return freq

            gap_scores = []
            numgaps = len(tokseqs) - 1

            # test values range(7, 8)
            for curr_gap in range(numgaps):
                score_dividend, score_divisor_b1, score_divisor_b2 = 0.0, 0.0, 0.0
                score = 0.0
                # adjust window size for boundary conditions
                if curr_gap < k - 1:
                    window_size = curr_gap + 1
                elif curr_gap > numgaps - k:
                    window_size = numgaps - curr_gap
                else:
                    window_size = k

                b1 = [ts.index for ts in tokseqs[curr_gap - window_size + 1 : curr_gap + 1]]
                b2 = [ts.index for ts in tokseqs[curr_gap + 1 : curr_gap + window_size + 1]]
                # windows are next to each other and max 10 elements long (parameter k)
                # every gap is once calculated
                # print(b1)

                # counter = 0
                for t in token_table:
                    # if counter > 20:
                    #     break
                    # counter += 1
                    score_dividend += blk_frq(t, b1) * blk_frq(t, b2) # words must at least occur once in each block to obtain values > 0
                    score_divisor_b1 += blk_frq(t, b1) ** 2
                    score_divisor_b2 += blk_frq(t, b2) ** 2

                #print("score ", score_dividend)
                #print("divisor b1 ", score_divisor_b1)
                #print("divisor b2 ", score_divisor_b2)

                try:
                    score = score_dividend / math.sqrt(score_divisor_b1 * score_divisor_b2)
                except ZeroDivisionError:
                    pass  # score += 0.0

                gap_scores.append(score)

            return gap_scores

    def _smooth_scores(gap_scores):
        "Wraps the smooth function from the SciPy Cookbook"
        return list(
            smooth(np.array(gap_scores[:]), window_len=smoothing_width + 1)
        )

    # Pasted from the SciPy cookbook: http://www.scipy.org/Cookbook/SignalSmooth
    def smooth(x, window_len=11, window="flat"):
        "smooth the data using a window with requested size."
        if x.ndim != 1:
            raise ValueError("smooth only accepts 1 dimension arrays.")

        if x.size < window_len:
            raise ValueError("Input vector needs to be bigger than window size.")

        if window_len < 3:
            return x

        if window not in ["flat", "hanning", "hamming", "bartlett", "blackman"]:
            raise ValueError(
                "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"
            )

        s = np.r_[2 * x[0] - x[window_len:1:-1], x, 2 * x[-1] - x[-1:-window_len:-1]]

        # print(len(s))
        if window == "flat":  # moving average
            w = np.ones(window_len, "d")
        else:
            w = eval("np." + window + "(window_len)")

        y = np.convolve(w / w.sum(), s, mode="same")

        return y[window_len - 1 : -window_len + 1]

    def _depth_scores(scores):
        """Calculates the depth of each gap, i.e. the average difference
        between the left and right peaks and the gap's score"""

        depth_scores = [0 for x in scores]
        # clip boundaries: this holds on the rule of thumb(my thumb)
        # that a section shouldn't be smaller than at least 2
        # pseudosentences for small texts and around 5 for larger ones.

        clip = min(max(len(scores) // 10, 2), 5)
        index = clip

        for gapscore in scores[clip:-clip]:
            # print(scores[clip:-clip])
            # print("gapscore ", gapscore)
            lpeak = gapscore
            for score in scores[index::-1]: # climbs up to the highest peak on the left starting from the current gapscore
                #print("left ", scores[index::-1])
                #print("score ", score)
                if score >= lpeak:
                    #print(score, " >= ", lpeak)
                    lpeak = score
                    #print("new peak", lpeak)
                else:
                    break
            rpeak = gapscore
            for score in scores[index:]: # climbs up to the highest peak on the right starting from the current gapscore
                # print("right ", scores[index:])
                # print("right ", score)
                if score >= rpeak:
                    # print(score, " >= ", rpeak)
                    rpeak = score
                    # print("new peak", rpeak)
                else:
                    break
            depth_scores[index] = lpeak + rpeak - 2 * gapscore
            index += 1
        
        return depth_scores

    class TokenSequence(object):
        "A token list with its original length and its index"
        def __init__(self, index, wrdindex_list, original_length=None):
            original_length = original_length or len(wrdindex_list) # if no value is specified, len(wrdindex_list) is used
            self.__dict__.update(locals()) # make input variables to class variables (self.variable)
            del self.__dict__["self"] # delete self, otherwise self.self would be possible

    class TokenTableField(object):
        """A field in the token table holding parameters for each token,
        used later in the process"""
        def __init__(
            self,
            first_pos,
            ts_occurences,
            total_count=1,
            par_count=1,
            last_par=0,
            last_tok_seq=None,
        ):
            self.__dict__.update(locals())
            del self.__dict__["self"]

    ### Hyperparameters

    w = 20
    k = 10
    sw = stopwords.words("english")
    smoothing_width=2

    lowercase_text = text.lower()
    paragraph_breaks = _mark_paragraph_breaks(text)
    text_length = len(lowercase_text)

    nopunct_text = "".join(c for c in lowercase_text if re.match("[a-z\-' \n\t]", c)) # removes punctuation
    nopunct_par_breaks = _mark_paragraph_breaks(nopunct_text)

    tokseqs = _divide_to_tokensequences(nopunct_text)

    ## Filter stopwords
    for ts in tokseqs:
        ts.wrdindex_list = [wi for wi in ts.wrdindex_list if wi[0] not in sw]

    token_table = _create_token_table(tokseqs, nopunct_par_breaks)

    gap_scores = _block_comparison(tokseqs, token_table)
    # print(gap_scores)

    smooth_scores = _smooth_scores(gap_scores)

    depth_scores = _depth_scores(smooth_scores)

    #fig = go.Figure()

    # fig.add_trace(go.Scatter(
    #     x=[1, 2, 3],
    #     y=[1, 4, 9],
    #     mode="text",
    #     name="Lines, Markers and Text",
    #     text=["Text A", "Text B", "Text C"],
    #     textposition="middle center"
    # ))

    x = range(len(depth_scores))
    y = depth_scores
    fig = px.line(x=x, y=y)

    x2 = range(len(smooth_scores))
    y2 = smooth_scores
    fig2 = px.line(x=x2, y=y2)
    
    return fig2, fig


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
 
    try:
        df = pd.read_csv(
            filepath_or_buffer=io.StringIO(decoded.decode('utf-8')),
            header=0,
            names=["Speaker", "Time", "End time", "Duration", "Utterance"],
            usecols=["Speaker", "Time", "Utterance"]
        )
        
    except Exception as e:
        return html.Div(['There was an error processing this file.'])
        
    return df


@app.callback(
    Output(component_id="transcript_selector", component_property="options"),
    Output(component_id ="modal_upload", component_property="is_open"),
    Output("output_file", "children"),
    Input(component_id="upload_input", component_property="contents"),
    Input(component_id="close", component_property="n_clicks"),
    State(component_id="upload_input", component_property="filename"),
    State(component_id="upload_input", component_property="last_modified"),
    State(component_id="modal_upload", component_property="is_open"))

def update_transcripts(list_of_contents, modal_upload_input, list_of_names, list_of_dates, is_open):
    if is_open == True:
        return dash.no_update, False, ""

    if list_of_contents is not None:
        transcript = parse_contents(list_of_contents, list_of_names, list_of_dates)
        
        transcript["Time"] = transcript["Time"].str.replace("60", "59")
        calculate_timestamps(transcript)
        
        transcripts.append(transcript)
        transcripts_files.append(list_of_names)

        output_name = list_of_names[:-4] + " is now available in the Dropdown Menue"
        return [{"label": transcripts_files[i], "value": i} for i in range(len(transcripts_files))], True, output_name

    return [{"label": transcripts_files[i], "value": i} for i in range(len(transcripts_files))], False, ""






# @app.callback(
#     Output(component_id="keyword_table", component_property="children"),
#     Input(component_id="transcript_selector", component_property="value"),
#     Input(component_id="keyword_extraction_apply_button", component_property="n_clicks"),
#     State(component_id="keyword_extraction_method_selector", component_property="value"),
# )
# def extract_keywords(selected_transcript, n_clicks, selected_methods):
#     transcript = pd.read_csv("./transcripts/" + selected_transcript)

#     if dash.callback_context.triggered[0]["prop_id"] == "keyword_extraction_apply_button.n_clicks":

#         if "textrank" in selected_methods:
#             textrank_keywords = [None] * len(transcript)
#             for i in range(len(transcript)):
#                 try:
#                     textrank_keywords[i] = keywords.keywords(transcript.text[i], words=3).replace("\n", ", ")
#                 except:
#                     textrank_keywords[i] = ""
#             transcript["textrank"] = textrank_keywords

#         # if "topicrank" in selected_methods:
#         #     topicrank_keywords = [None] * len(transcript)
#         #     for i in range(len(transcript)):
#         #         try:
#         #             topicrank_keywords[i] = ", ".join(TopicRank(transcript.text[i]).get_top_n(3))
#         #         except:
#         #             topicrank_keywords[i] = ""
#         #     transcript["topicrank"] = topicrank_keywords

#     transcript.drop(columns=["text"], inplace=True)
#     return dbc.Table.from_dataframe(transcript, bordered=True, hover=True)

# @app.callback(
#     Output(component_id="speakers_ratio", component_property="figure"),
#     Input(component_id="transcript_selector", component_property="value"),
# )
# def plot_speakers_ratio(selected_transcript):

#     transcript = pd.read_csv("./transcripts/" + selected_transcript)

#     transcript["word_count"] = 0
#     for i in range(len(transcript)):
#         transcript["word_count"][i] = len(transcript["text"][i].split())

#     words_spoken = transcript.groupby(["speaker"]).sum()
#     words_spoken.reset_index(inplace=True)

#     fig = px.bar(words_spoken, x = "speaker", y = "word_count", title="Speaker ratio")
    
#     return fig

if __name__ == "__main__":
    # context = ("/etc/letsencrypt/live/projects.pascalaigner.ch/cert.pem", "/etc/letsencrypt/live/projects.pascalaigner.ch/privkey.pem")
    app.run_server(
        # host="projects.pascalaigner.ch",
        # port=443,
        # ssl_context=context,
        debug=True)
