import sys
import os

sys.path.insert(0, os.path.split(os.path.split(sys.path[0])[0])[0])
path = sys.path[0]

import plotly
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

pio.kaleido.scope.default_format = "png"
pio.kaleido.scope.default_width = 1920
pio.kaleido.scope.default_height = 500

timestamps_human = ["00:00", "12:53", "17:37", "22:06", "32:36", "41:09", "44:21"]
timestamps_texttiling = ["00:00", "13:47", "20:03", "29:59", "36:43", "44:21"]
timestamps_textsplit = ["00:00", "17:58", "21:51", "30:41", "32:26", "37:08", "44:21"]

def convert_to_seconds(t):
    return int(t[:2])*60 + int(t[3:])

timestamps_human_s = [convert_to_seconds(t) for t in timestamps_human]
timestamps_texttiling_s = [convert_to_seconds(t) for t in timestamps_texttiling]
timestamps_textsplit_s = [convert_to_seconds(t) for t in timestamps_textsplit]

last_min = int(timestamps_human[-1][:2])
ticks = list(range(0, last_min, 5))

y_position = [0.15, 0.3, 0.45]

fig = go.Figure()
fig["layout"] = go.Layout(margin={"t": 0, "b": 0, "r": 0, "l": 0}, plot_bgcolor="rgba(0,0,0,0)")

fig.add_trace(go.Scatter(
    x=timestamps_human_s,
    y=[y_position[2]] * len(timestamps_human_s),
    mode="lines",
    line=dict(
        width=4,
        color="#4472C4",
    ),
    name="Human",
))
for i in range(1, len(timestamps_human_s)-1):
    fig.add_shape(
        type="line",
        x0=timestamps_human_s[i],
        y0=y_position[2]-0.05,
        x1=timestamps_human_s[i],
        y1=y_position[2]+0.05,
        line=dict(
            width=3,
            dash="dot",
            color="#4472C4",
    ))

fig.add_trace(go.Scatter(
    x=timestamps_texttiling_s ,
    y=[y_position[1]] * len(timestamps_texttiling_s ),
    mode="lines",
    line=dict(
        width=4,
        color="#ED7D31",
    ),
    name="TextTiling",
))
for i in range(1, len(timestamps_texttiling_s )-1):
    fig.add_shape(
        type="line",
        x0=timestamps_texttiling_s [i],
        y0=y_position[1]-0.05,
        x1=timestamps_texttiling_s [i],
        y1=y_position[1]+0.05,
        line=dict(
            width=3,
            dash="dot",
            color="#ED7D31",
    ))

fig.add_trace(go.Scatter(
    x=timestamps_textsplit_s,
    y=[y_position[0]] * len(timestamps_textsplit_s ),
    mode="lines",
    line=dict(
        width=4,
        color="#2ca02c",
    ),
    name="Textsplit",
))
for i in range(1, len(timestamps_textsplit_s )-1):
    fig.add_shape(
        type="line",
        x0=timestamps_textsplit_s [i],
        y0=y_position[0]-0.05,
        x1=timestamps_textsplit_s [i],
        y1=y_position[0]+0.05,
        line=dict(
            width=3,
            dash="dot",
            color="#2ca02c",
    ))


axes_title_font = dict(family="Times", size=50)
axes_tick_font = dict(family="Times", size=40)
space_between_axis_label_and_ticks = 40
grid_line_width = 4
fig.update_xaxes(
    title="Duration in minutes",
    title_font=axes_title_font,
    title_standoff=space_between_axis_label_and_ticks,
    zerolinewidth=grid_line_width,
    linecolor="black",
    ticks="outside",
    tickson="boundaries",
    tickcolor="black",
    ticklen=20,
    gridwidth=grid_line_width,
    tickfont=axes_tick_font,
    tick0=0,
    dtick=300,
    ticktext = ticks,
    tickvals = list(range(0, 300*len(ticks), 300)),
)
fig.update_yaxes(
    range=[0,1],
    visible = False
)
fig.update_layout(
    legend=dict(
        yanchor="top",
        xanchor="right",
        x=1,
        y=0.7,
        orientation="h",
    ),
    font=axes_tick_font
)
# fig.show()
fig.write_image(path + "/Images in paper/Topic Segmentation Results/debate.png")
