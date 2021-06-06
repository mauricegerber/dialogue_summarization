import plotly
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import numpy as np
import math
pio.kaleido.scope.default_format = "png"
pio.kaleido.scope.default_width = 1920
pio.kaleido.scope.default_height = 500

timestamps_human = ["00:00", "03:13", "05:13", "10:00"]
timestamps_texttiling = ["00:00", "04:14", "10:00"]
timestamps_textsplit = ["00:00", "05:15", "10:00"]

def convert_to_seconds(t):
    return int(t[:2])*60 + int(t[3:])


timestamps_human_s = [convert_to_seconds(t) for t in timestamps_human]
timestamps_texttiling_s = [convert_to_seconds(t) for t in timestamps_human]
timestamps_textsplit_s = [convert_to_seconds(t) for t in timestamps_human]

# end_transcript = "12:23"
# con_end = convert_to_seconds(end_transcript)
# time_seq = np.linspace(0, con_end, 7)
# print(list(time_seq))
# ticks={i: str(math.floor(time_seq[i]/60))+str(math.floor(math.modf(time_seq[i]/60)[0]*60))
#     +" min" for i in range(1,len(time_seq))}

# print(ticks)

y_position = [0.35, 0.5, 0.65]

fig = go.Figure()
fig["layout"] = go.Layout(margin={"t": 0, "b": 0, "r": 0, "l": 0}, plot_bgcolor="rgba(0,0,0,0)")

fig.add_trace(go.Scatter(
    x=timestamps_human_s,
    y=[y_position[2]] * len(timestamps_human_s),
    mode="lines",
    line=dict(width=4)
))
for i in range(1, len(timestamps_human_s)-1):
    fig.add_shape(
        type="line",
        x0=timestamps_human_s[i],
        y0=y_position[2]-0.05,
        x1=timestamps_human_s[i],
        y1=y_position[2]+0.05,
        line=dict(
            color="DarkOrange",
            width=3,
            dash="dot",
    ))

fig.add_trace(go.Scatter(
    x=timestamps_texttiling_s ,
    y=[y_position[1]] * len(timestamps_texttiling_s ),
    mode="lines",
    line=dict(width=4)
))
for i in range(1, len(timestamps_texttiling_s )-1):
    fig.add_shape(
        type="line",
        x0=timestamps_texttiling_s [i],
        y0=y_position[1]-0.05,
        x1=timestamps_texttiling_s [i],
        y1=y_position[1]+0.05,
        line=dict(
            color="DarkOrange",
            width=3,
            dash="dot",
    ))

fig.add_trace(go.Scatter(
    x=timestamps_textsplit_s,
    y=[y_position[0]] * len(timestamps_textsplit_s ),
    mode="lines",
    line=dict(width=4)
))
for i in range(1, len(timestamps_textsplit_s )-1):
    fig.add_shape(
        type="line",
        x0=timestamps_textsplit_s [i],
        y0=y_position[0]-0.05,
        x1=timestamps_textsplit_s [i],
        y1=y_position[0]+0.05,
        line=dict(
            color="DarkOrange",
            width=3,
            dash="dot",
    ))


axes_title_font = dict(family="Times", size=50)
axes_tick_font = dict(family="Times", size=40)
space_between_axis_label_and_ticks = 40
grid_line_width = 4
fig.update_xaxes(
    title="Gap",
    title_font=axes_title_font,
    title_standoff=space_between_axis_label_and_ticks,
    zerolinewidth=grid_line_width,
    gridwidth=grid_line_width,
    tickfont=axes_tick_font
)
fig.update_yaxes(
    range=[0,1],
    title="Score",
    title_font=axes_title_font,
    title_standoff=space_between_axis_label_and_ticks,
    zerolinewidth=grid_line_width,
    gridwidth=grid_line_width,
    tickfont=axes_tick_font,
    tick0=0,
    dtick=0.1,
    visible = False
)
fig.show()
# fig.write_image("./Algorithms/texttiling_gap_score.png")