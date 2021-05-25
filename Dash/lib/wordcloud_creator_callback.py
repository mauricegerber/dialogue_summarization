import sys

import dash
from dash.dependencies import Input, Output, State

sys.path.insert(0, "./lib")
import split_dialog
import wordcloud_pl

def wordcloud_creator(app, transcripts):
    @app.callback(
        Output(component_id="wordcloud_plot", component_property="figure"),
        Output(component_id="vertical_slider", component_property="style"),
        Output(component_id="wordcloud_steps_slider", component_property="max"),
        Output(component_id="wordcloud_steps_slider", component_property="value"),
        Output(component_id="wordcloud_steps_slider", component_property="marks"),
        Input(component_id="apply_wordcloud_settings", component_property="n_clicks"),
        Input(component_id="transcript_selector", component_property="value"),
        Input(component_id="wordcloud_steps_slider", component_property="value"),
        Input(component_id="textblock_length_input", component_property="value"),
    )
    def wordcloud_creator(n_clicks, selected_transcript, section, slct_min):
        
        if dash.callback_context.triggered[0]["prop_id"] == "apply_wordcloud_settings.n_clicks":
            transcript = transcripts[int(selected_transcript)]
            data = transcript.to_dict("records")

            words, min_seq, counts = split_dialog.split_dialog(data, slct_min)
            
            min_rev = list(min_seq)[::-1]
            marks={i-1: str(min_rev[i])+"-"+str(min_rev[i-1])+" min" for i in range(1,len(min_seq))}
            
            max_section = len(words)-1
            current_section = max_section
            
            dict_selected = words[0]
            ldict = len(dict_selected)
            
            fig = wordcloud_pl.plot(dict_selected, ldict)
            
            return fig, {"visibility": "visible"}, max_section, current_section, marks
        

        if dash.callback_context.triggered[0]["prop_id"] == "wordcloud_steps_slider.value":    
            transcript = transcripts[int(selected_transcript)]
            data = transcript.to_dict("records")

            words, min_seq, counts = split_dialog.split_dialog(data, slct_min)

            max_section = len(words)-1
            current_section = abs(section - max_section)
            
            dict_selected = words[current_section]
            ldict = len(dict_selected)

            fig = wordcloud_pl.plot(dict_selected, ldict)

            return fig, dash.no_update, dash.no_update, dash.no_update, dash.no_update

        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update