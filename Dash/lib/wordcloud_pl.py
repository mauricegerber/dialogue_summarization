import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import scipy.special as sc

def plot(dict_selected, ldict):
    size_multiplier = 4
    for key in dict_selected.keys():
        dict_selected[key] = dict_selected[key] * size_multiplier
    
    coordX = []
    coordY = []
    
    def sample(center,radius,n_per_sphere):
        r = radius
        ndim = center.size
        x = np.random.normal(size=(n_per_sphere, ndim))
        ssq = np.sum(x**2,axis=1)
        fr = r*sc.gammainc(ndim/2,ssq/2)**(1/ndim)/np.sqrt(ssq)
        frtiled = np.tile(fr.reshape(n_per_sphere,1),(1,ndim))
        p = center + np.multiply(x,frtiled)
        return p
    ok = sample(np.array([0,0]), 1, ldict)

    coordX = ok[:,0]
    coordY = ok[:,1]

    # xcord = []
    # for i in range(ldict):
    #     xcord.append(i*0.2)
    # ycord = [2] * ldict

    size = list(dict_selected.values())
    word = list(dict_selected.keys())
    
    fig = go.Figure()

    fig.add_trace(go.Scatter(
    x=coordX ,
    y=coordY ,
    mode="text",
    name="Text",
    text=word,
    textposition="top center",
    textfont=dict(size=size)
    ))

    fig["layout"] = go.Layout(margin={'t': 0, "b":0, "r":0, "l":0})

    return fig