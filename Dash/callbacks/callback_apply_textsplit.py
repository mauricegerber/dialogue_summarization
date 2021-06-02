import pandas as pd
import string

import dash
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from rake_nltk import Rake
from yake import KeywordExtractor
from keybert import KeyBERT

# import functions
from functions.textsplit import textsplit
from functions.tfidf import tfidf

def callback_apply_textsplit(app, transcripts):
    @app.callback(
        Output(component_id="textsplit_plot", component_property="figure"),
        Output(component_id="textsplit_table", component_property="data"),
        Output(component_id="textsplit_table", component_property="columns"),
        Output(component_id="textsplit_table", component_property="style_cell_conditional"),
        Input(component_id="apply_textsplit_settings", component_property="n_clicks"),
        State(component_id="transcript_selector", component_property="value"),
        State(component_id="break_condition_radio_button", component_property="value"),
        State(component_id="max_splits_input", component_property="value"),
        State(component_id="min_gain_input", component_property="value"),
        State(component_id="keyword_extraction_method_selector", component_property="value"),
        State(component_id="language_radio_button", component_property="value"),
        State(component_id="tfidf_n_kws", component_property="value"),
        State(component_id="tfidf_radio_button", component_property="value"),
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
    def apply_textsplit(n_clicks, selected_transcript, selected_break_condition, max_splits, min_gain,
                        selected_methods, selected_language, tfidf_n_kws, tfidf_method,
                        rake_n_kws, rake_min_kw_len, rake_max_kw_len,
                        yake_n_kws, yake_max_kw_len, yake_dd_threshold,
                        keybert_n_kws, keybert_min_kw_len, keybert_max_kw_len, keybert_diversity):
        if dash.callback_context.triggered[0]["prop_id"] == "apply_textsplit_settings.n_clicks":
            transcript = transcripts[int(selected_transcript)]

            if selected_break_condition == "max_splits":
                normalized_splits, splits, lengths_optimal = textsplit(transcript, max_splits-1, None)
            if selected_break_condition == "min_gain":
                normalized_splits, splits, lengths_optimal = textsplit(transcript, None, min_gain)

            boundaries_timestamps = [transcript["Timestamp"][i] for i in normalized_splits]
            boundaries_time = [transcript["Time"][normalized_splits[i-1]] + " - " + transcript["Time"][normalized_splits[i]]
                            for i in range(1, len(normalized_splits))]
            
            subtopics = []
            for i in range(1, len(boundaries_timestamps)):
                transcript_subtopic = transcript[transcript["Timestamp"] < boundaries_timestamps[i]]
                transcript_subtopic = transcript_subtopic[transcript_subtopic["Timestamp"] >= boundaries_timestamps[i-1]]
                text = ""
                for utterance in transcript_subtopic["Utterance"].str.lower():
                    text += utterance
                subtopics.append(text)
                
            data = {"Start time": boundaries_time}
            keywords_table = pd.DataFrame(data=data)
            current_columns = [{"name": "Time", "id": "Start time", "presentation": "markdown"}]
            column_names = ["Start time"]
            width = "50px"
            current_style=[{"if": {"column_id": "Start time"}, "width": "30px"}]

            if "tf-idf" in selected_methods:

                if tfidf_method == "karen_jones":
                    df = tfidf(subtopics)
                else:
                    vectorizer = TfidfVectorizer()
                    vectors = vectorizer.fit_transform(subtopics)
                    feature_names = vectorizer.get_feature_names()
                    dense = vectors.todense()
                    denselist = dense.tolist()
                    df = pd.DataFrame(denselist, columns=feature_names).transpose()
                
                tf_idf_keywords = []
                for column in df:
                    tf_idf_keywords.append(", ".join(list(df[column].sort_values(ascending=False).index[:tfidf_n_kws])))

                for i in range(len(tf_idf_keywords)):
                    tokens = word_tokenize(subtopics[i])
                    tokens = [s.translate(str.maketrans("", "", string.punctuation)) for s in tokens]
                    if len(tokens) < tfidf_n_kws+1:
                        tf_idf_keywords[i] = ""
                keywords_table["tf-idf"] = tf_idf_keywords
                if "tf-idf" not in current_columns and "tf-idf" not in column_names:
                    current_columns.append({"name": "tf-idf", "id": "tf-idf", "presentation": "markdown"})
                    column_names.append("tf-idf")
                    current_style.append({"if": {"column_id": "tf-idf"}, "width": width})

            if "tf-idf" not in selected_methods:
                try:
                    keywords_table.drop(columns=["tf-idf"], inplace=True)
                    current_columns.remove({"name": "tf-idf", "id": "tf-idf", "presentation": "markdown"})
                    column_names.remove("tf-idf")
                    current_style.remove({"if": {"column_id": "tf-idf"}, "width": width})
                except:
                    pass

            if "rake" in selected_methods:
                r = Rake(language=selected_language, min_length=rake_min_kw_len, max_length=rake_max_kw_len)
                rake_keywords = []
                for subtopic in subtopics:
                    r.extract_keywords_from_text(subtopic)
                    rake_keywords.append(", ".join(r.get_ranked_phrases()[:rake_n_kws]))
                keywords_table["rake"] = rake_keywords
                if "rake" not in current_columns and "rake" not in column_names and "rake":
                    current_columns.append({"name": "rake", "id": "rake", "presentation": "markdown"})
                    column_names.append("rake")
                    current_style.append({"if": {"column_id": "rake"}, "width": width})

            if "rake" not in selected_methods:
                try:
                    keywords_table.drop(columns=["rake"], inplace=True)
                    current_columns.remove({"name": "rake", "id": "rake", "presentation": "markdown"})
                    column_names.remove("rake")
                    current_style.remove({"if": {"column_id": "rake"}, "width": width})
                except:
                    pass

            if "yake" in selected_methods:
                if selected_language == "english":
                    lan = "en"
                else:
                    lan = "de"
                kw_extractor = KeywordExtractor(lan=lan, top=yake_n_kws, n=yake_max_kw_len, dedupLim=yake_dd_threshold)
                yake_keywords = []
                for subtopic in subtopics:
                    keywords = kw_extractor.extract_keywords(text=subtopic)
                    if yake_dd_threshold < 1:
                        keywords = [x for x, y in keywords]
                    else:
                        keywords = [y for x, y in keywords]
                    yake_keywords.append(", ".join(keywords))
                keywords_table["yake"] = yake_keywords
                if "yake" not in current_columns and "yake" not in column_names and "yake":
                    current_columns.append({"name": "yake", "id": "yake", "presentation": "markdown"})
                    column_names.append("yake")
                    current_style.append({"if": {"column_id": "yake"}, "width": width})

            if "yake" not in selected_methods:
                try:
                    keywords_table.drop(columns=["yake"], inplace=True)
                    current_columns.remove({"name": "yake", "id": "yake", "presentation": "markdown"})
                    column_names.remove("yake")
                    current_style.remove({"if": {"column_id": "yake"}, "width": width})
                except:
                    pass
            
            if "keybert" in selected_methods:
                sw = stopwords.words(selected_language)
                kw_extractor = KeyBERT("distilbert-base-nli-mean-tokens")
                kerybert_keywords = []
                for subtopic in subtopics:
                    keywords = kw_extractor.extract_keywords(subtopic, stop_words=sw, use_mmr=True,
                                                             keyphrase_ngram_range=(keybert_min_kw_len, keybert_max_kw_len),
                                                             diversity=keybert_diversity)
                    keywords = [w for w, v in keywords]
                    kerybert_keywords.append(", ".join(keywords[:keybert_n_kws]))
                keywords_table["keybert"] = kerybert_keywords
                if "keybert" not in current_columns and "keybert" not in column_names and "keybert":
                    current_columns.append({"name": "keybert", "id": "keybert", "presentation": "markdown"})
                    column_names.append("keybert")
                    current_style.append({"if": {"column_id": "tf-idf"}, "width": width})
                    current_style.append({"if": {"column_id": "keybert"}, "width": width})

            if "keybert" not in selected_methods:
                try:
                    keywords_table.drop(columns=["keybert"], inplace=True)
                    current_columns.remove({"name": "keybert", "id": "keybert", "presentation": "markdown"})
                    column_names.remove("keybert")
                    current_style.remove({"if": {"column_id": "keybert"}, "width": width})
                except:
                    pass

            fig = go.Figure()
            fig["layout"] = go.Layout(margin={"t": 0, "b": 0, "r": 0, "l": 0})
            for i in range(len(splits)):
                fig.add_shape(
                    type="line",
                    x0=splits[i],
                    y0=0,
                    x1=splits[i],
                    y1=max(lengths_optimal),
                    line=dict(
                        color="DarkOrange",
                        width=3,
                        dash="dot",
                ))
                fig.add_annotation(
                    x=splits[i],
                    y=max(lengths_optimal)+max(lengths_optimal)*0.1,
                    text=transcript["Time"][normalized_splits[i+1]],
                    showarrow=False,
                )
            fig.add_trace(go.Scatter(
                x=list(range(len(lengths_optimal))),
                y=lengths_optimal,
                mode="lines"
            ))
            fig.update_layout(
                xaxis_title="Sentence",
                yaxis_title="Subtopic length",
            )

            return fig, keywords_table[column_names].to_dict("records"), current_columns, current_style

        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
