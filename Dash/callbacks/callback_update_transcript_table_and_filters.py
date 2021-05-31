import math
import string
import time
from datetime import datetime

import dash
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go

from nltk.tokenize import word_tokenize
from rake_nltk import Rake
from yake import KeywordExtractor
from keybert import KeyBERT

# import functions
from functions.tfidf import tfidf

def callback_update_transcript_table_and_filters(app, transcripts):
    @app.callback(
        Output(component_id="transcript_table", component_property="columns"),
        Output(component_id="transcript_table", component_property="data"),
        Output(component_id="transcript_table", component_property="style_cell_conditional"),
        Output(component_id="transcript_table", component_property="css"),
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
        Input(component_id="apply_keyword_extraction_settings", component_property="n_clicks"),
        State(component_id="keyword_extraction_method_selector", component_property="value"),
        State(component_id="transcript_table", component_property="columns"),
        State(component_id="transcript_table", component_property="style_cell_conditional"),
        State(component_id="language_radio_button", component_property="value"),
        State(component_id="rake_n_kws", component_property="value"),
        State(component_id="rake_min_kw_len", component_property="value"),
        State(component_id="rake_max_kw_len", component_property="value"),
        State(component_id="yake_n_kws", component_property="value"),
        State(component_id="yake_max_kw_len", component_property="value"),
        State(component_id="yake_dd_threshold", component_property="value"),
        State(component_id="keybert_n_kws", component_property="value"),
        State(component_id="keybert_min_kw_len", component_property="value"),
        State(component_id="keybert_max_kw_len", component_property="value"),
        State(component_id="keybert_diversity", component_property="value"),
    )
    def update_transcript_table_and_filters(selected_transcript, selected_speaker, selected_start_time,
                                            selected_end_time, selected_timeline, search_term,
                                            n_clicks, selected_methods, current_columns, current_style,
                                            selected_language, rake_n_kws, rake_min_kw_len, rake_max_kw_len,
                                            yake_n_kws, yake_max_kw_len, yake_dd_threshold,
                                            keybert_n_kws, keybert_min_kw_len, keybert_max_kw_len, keybert_diversity):
        transcript = transcripts[int(selected_transcript)]

        timeline_min = transcript["Timestamp"][0]
        timeline_max = transcript["Timestamp"][len(transcript)-1]
        # difference between timeline_max and start of last minute, e.g. 44:21 - 44:00 = 00:21
        timeline_deviation = timeline_max - math.floor(timeline_max/60)*60
        marks = dict()

        trigger = dash.callback_context.triggered[0]["prop_id"]

        if trigger == "transcript_selector.value":
            speakers = transcript["Speaker"].unique()
            transcript_table = transcript[["Speaker", "Time", "Utterance"]].to_dict("records")
            columns = [
                {"name": "Speaker", "id": "Speaker", "presentation": "markdown"},
                {"name": "Time", "id": "Time", "presentation": "markdown"},
                {"name": "Utterance", "id": "Utterance", "presentation": "markdown"},
            ]
            style_cell_conditional=[
                {"if": {"column_id": "Speaker"},
                "width": "30px"},
                {"if": {"column_id": "Time"},
                "width": "30px"},
                {"if": {"column_id": "Utterance"},
                "width": "800px"},
            ]

            # set height of transcript table depending on height of filter section
            if len(speakers) == 2:
                filter_section_height = 73
            elif len(speakers) == 3:
                filter_section_height = 90
            else:
                filter_section_height = 90 + (len(speakers)-3) * 21
            transcript_table_height = 30+38+30+52+15+38+15+filter_section_height+15+15+21+15
            css_code = "max-height: calc(100vh - " + str(transcript_table_height) + "px)"
            
            return (columns, transcript_table, style_cell_conditional, [{"selector": ".dash-freeze-top", "rule": css_code}],
                    [{"label": i, "value": i} for i in sorted(speakers, key=str.lower)], speakers,
                    "00:00", time.strftime("%H:%M", time.gmtime(timeline_max)),
                    timeline_min, timeline_max, [timeline_min, timeline_max], marks, None)

        if trigger == "apply_keyword_extraction_settings.n_clicks":
            column_names = [column["name"] for column in current_columns]
            n_keywords = 3
            width = "50px"

            if "tf-idf" in selected_methods and "tf-idf" not in column_names:
                documents = transcript["Utterance"].str.lower().tolist()
                df = tfidf(documents)
                tf_idf_keywords = []
                for column in df:
                    tf_idf_keywords.append(", ".join(list(df[column].sort_values(ascending=False).index[:n_keywords])))

                for i in range(len(tf_idf_keywords)):
                    tokens = word_tokenize(transcript["Utterance"].iloc[i])
                    tokens = [s.translate(str.maketrans("", "", string.punctuation)) for s in tokens]
                    if len(tokens) < n_keywords+1:
                        tf_idf_keywords[i] = ""
                transcript["tf-idf"] = tf_idf_keywords
                current_columns.append({"name": "tf-idf", "id": "tf-idf", "presentation": "markdown"})
                column_names.append("tf-idf")
                current_style.append({"if": {"column_id": "tf-idf"}, "width": width})

            if "tf-idf" not in selected_methods:
                try:
                    transcript.drop(columns=["tf-idf"], inplace=True)
                    current_columns.remove({"name": "tf-idf", "id": "tf-idf", "presentation": "markdown"})
                    column_names.remove("tf-idf")
                    current_style.remove({"if": {"column_id": "tf-idf"}, "width": width})
                except:
                    pass

            if "rake" in selected_methods:
                r = Rake(language=selected_language, min_length=rake_min_kw_len, max_length=rake_max_kw_len)
                rake_keywords = []
                for utterance in transcript["Utterance"]:
                    r.extract_keywords_from_text(utterance)
                    rake_keywords.append(", ".join(r.get_ranked_phrases()[:rake_n_kws]))
                transcript["rake"] = rake_keywords
                if "rake" not in current_columns and "rake" not in column_names and "rake" not in current_style:
                    current_columns.append({"name": "rake", "id": "rake", "presentation": "markdown"})
                    column_names.append("rake")
                    current_style.append({"if": {"column_id": "rake"}, "width": width})

            if "rake" not in selected_methods:
                try:
                    transcript.drop(columns=["rake"], inplace=True)
                    current_columns.remove({"name": "rake", "id": "rake", "presentation": "markdown"})
                    column_names.remove("rake")
                    current_style.remove({"if": {"column_id": "rake"}, "width": width})
                except:
                    pass

            if "yake" in selected_methods:
                kw_extractor = KeywordExtractor(lan=selected_language, top=yake_n_kws, n=yake_max_kw_len, dedupLim=yake_dd_threshold)
                yake_keywords = []
                for utterance in transcript["Utterance"]:
                    keywords = kw_extractor.extract_keywords(text=utterance)
                    keywords = [x for x, y in keywords]
                    yake_keywords.append(", ".join(keywords))
                transcript["yake"] = yake_keywords
                if "yake" not in current_columns and "yake" not in column_names and "yake" not in current_style:
                    current_columns.append({"name": "yake", "id": "yake", "presentation": "markdown"})
                    column_names.append("yake")
                    current_style.append({"if": {"column_id": "yake"}, "width": width})

            if "yake" not in selected_methods:
                try:
                    transcript.drop(columns=["yake"], inplace=True)
                    current_columns.remove({"name": "yake", "id": "yake", "presentation": "markdown"})
                    column_names.remove("yake")
                    current_style.remove({"if": {"column_id": "yake"}, "width": width})
                except:
                    pass
            
            if "keybert" in selected_methods:
                kw_extractor = KeyBERT("distilbert-base-nli-mean-tokens")
                kerybert_keywords = []
                for utterance in transcript["Utterance"]:
                    keywords = kw_extractor.extract_keywords(utterance, stop_words=selected_language, use_mmr=False,
                                                             keyphrase_ngram_range=(keybert_min_kw_len, keybert_max_kw_len),
                                                             diversity=keybert_diversity)
                    keywords = [w for w, v in keywords]
                    kerybert_keywords.append(", ".join(keywords[:keybert_n_kws]))
                transcript["keybert"] = kerybert_keywords
                if "keybert" not in current_columns and "keybert" not in column_names and "keybert" not in current_style:
                    current_columns.append({"name": "keybert", "id": "keybert", "presentation": "markdown"})
                    column_names.append("keybert")
                    current_style.append({"if": {"column_id": "keybert"}, "width": width})

            if "keybert" not in selected_methods:
                try:
                    transcript.drop(columns=["keybert"], inplace=True)
                    current_columns.remove({"name": "keybert", "id": "keybert", "presentation": "markdown"})
                    column_names.remove("keybert")
                    current_style.remove({"if": {"column_id": "keybert"}, "width": width})
                except:
                    pass

            transcript_table = transcript[column_names].to_dict("records")

            return (current_columns, transcript_table, current_style, dash.no_update, dash.no_update, transcript["Speaker"].unique(),
                    "00:00", time.strftime("%H:%M", time.gmtime(timeline_max)), dash.no_update, dash.no_update,
                    [timeline_min, timeline_max], marks, None)
        
        if trigger != "." and trigger != "transcript_selector.value":
            transcript = transcript[transcript["Speaker"].isin(selected_speaker)]
            
            # if double letter occurs, word highlighting does not work properly due to markdown syntax
            # therefore, search is only enabled for search terms longer than 1 character
            if search_term != None and len(search_term) > 1:
                transcript = transcript[transcript["Utterance"].str.contains(search_term, case=False, regex=False)]
                # if last character in search_term is a space, word highlighting does not work properly due to markdown syntax
                # therefore, it is stripped while highlighting (but not in the search field)
                if search_term[-1] == " ":
                    transcript["Utterance"] = transcript["Utterance"].str.replace(search_term[:-1], "**" + search_term[:-1] + "**", case=False)
                    try:
                        transcript["tf-idf"] = transcript["tf-idf"].str.replace(search_term[:-1], "**" + search_term[:-1] + "**", case=False)
                        transcript["rake"] = transcript["rake"].str.replace(search_term[:-1], "**" + search_term[:-1] + "**", case=False)
                        transcript["yake"] = transcript["yake"].str.replace(search_term[:-1], "**" + search_term[:-1] + "**", case=False)
                        transcript["keybert"] = transcript["keybert"].str.replace(search_term[:-1], "**" + search_term[:-1] + "**", case=False)
                    except:
                        pass
                else:
                    transcript["Utterance"] = transcript["Utterance"].str.replace(search_term, "**" + search_term + "**", case=False)
                    try:
                        transcript["tf-idf"] = transcript["tf-idf"].str.replace(search_term, "**" + search_term + "**", case=False)
                        transcript["rake"] = transcript["rake"].str.replace(search_term, "**" + search_term + "**", case=False)
                        transcript["yake"] = transcript["yake"].str.replace(search_term, "**" + search_term + "**", case=False)
                        transcript["keybert"] = transcript["keybert"].str.replace(search_term, "**" + search_term + "**", case=False)
                    except:
                        pass
                marks = dict(zip(transcript["Timestamp"], ["|"] * len(transcript)))
                
            if trigger == "start_time_input.value" or trigger == "end_time_input.value":
                # in Firefox the input field can be cleared by clicking the encircled X (which cannot be hidden)
                # this causes an error with the datetime conversion and is therefore handled as exception
                try:
                    first_timestamp = datetime.strptime("00:00", "%M:%S")
                    current_start_time = datetime.strptime(selected_start_time, "%H:%M")
                    current_end_time = datetime.strptime(selected_end_time, "%H:%M")
                    # timeline_deviation is added to prevent last utterances from being filtered out
                    # e.g. if 00:44 is entered, utterances from 00:44:01 to 00:44:21 would be filtered out if timeline_deviation was not added
                    timeline_slider_values = [(current_start_time - first_timestamp).total_seconds(),
                                            (current_end_time - first_timestamp).total_seconds() + timeline_deviation]
                    transcript = transcript[transcript["Timestamp"] >= timeline_slider_values[0]]
                    transcript = transcript[transcript["Timestamp"] <= timeline_slider_values[1]]
                    transcript_table = transcript[list(transcript)].to_dict("records")

                    return (dash.no_update, transcript_table, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update,
                            dash.no_update, dash.no_update, dash.no_update, timeline_slider_values, dash.no_update, dash.no_update)
                except:
                    pass

            transcript = transcript[transcript["Timestamp"] >= selected_timeline[0]]
            transcript = transcript[transcript["Timestamp"] <= selected_timeline[1]]
            transcript_table = transcript[list(transcript)].to_dict("records")

            return (dash.no_update, transcript_table, dash.no_update, dash.no_update, dash.no_update, dash.no_update,
                    time.strftime("%H:%M", time.gmtime(selected_timeline[0])),
                    time.strftime("%H:%M", time.gmtime(selected_timeline[1])),
                    dash.no_update, dash.no_update, dash.no_update, marks, dash.no_update)

        return (dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update,
                dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update)