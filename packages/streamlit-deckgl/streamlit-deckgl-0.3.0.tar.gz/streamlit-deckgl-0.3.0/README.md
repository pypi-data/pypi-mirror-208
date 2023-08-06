# streamlit-deckgl

Streamlit component for deck.gl visualisation with bi-directional transport for onClick events.

## Installation instructions

```sh
pip install streamlit-deckgl
```

## Usage

There is one component function `st_deckgl` with function signature:

```
component_value=st_deckgl(deck, height=500, configuration=None, key="deck_gl", events=None, description=None)
```

### Parameters

    deck : pydeck.Deck instance
        The pydeck map to render.
    key : str, default "deck_gl"
        The key for the component. This must be unique for each map in the app.
    height : int, default 500
        The height of the map in pixels.
    events : list, default None
        A dict of events to listen for. Can be one or more of:
        - 'click'
        - 'hover'
        - 'drag'
    description : dict, default None
        A dictionary with additional description components to overlay on the map
        The keys are the position which can be one of 'top-right','top-left','bottom-right','bottom-left'
        The values are the html elements to place in each position
        Example {'top-right':<div>This is a nice map</div>}
    configuration : dict, default None
        A dictionary of configuration options for the map.

### Returns

    component_value : dict
        A dictionary containing the info dictionary of the event.

## Example

```python
import streamlit as st
import pydeck as pdk
import pandas as pd

from streamlit_deckgl import st_deckgl


st.write("## Example")

chart_data = pd.DataFrame(
    np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4], columns=["lat", "lon"]
)

r = pdk.Deck(
    initial_view_state=pdk.ViewState(
        latitude=37.76, longitude=-122.4, zoom=11, pitch=50, height=600
    ),
    layers=[
        pdk.Layer(
            "HexagonLayer",
            data=chart_data,
            get_position="[lon, lat]",
            radius=200,
            elevation_scale=4,
            elevation_range=[0, 1000],
            pickable=True,
            extruded=True,
        ),
        pdk.Layer(
            "ScatterplotLayer",
            data=chart_data,
            get_position="[lon, lat]",
            get_color="[200, 30, 0, 160]",
            get_radius=200,
        ),
    ],
    tooltip={
        "html": "<b>Temperature:</b> {value} °C",
        "style": {"backgroundColor": "steelblue", "color": "white"},
    },
)

value = st_deckgl(r,)

st.write(value)
```
