from pathlib import Path
from typing import Optional, Dict

import streamlit as st
import streamlit.components.v1 as components

import pydeck as pdk

# Tell streamlit that there is a component called streamlit_deckgl,
# and that the code to display that component is in the "frontend" folder
frontend_dir = (Path(__file__).parent / "frontend").absolute()
_component_func = components.declare_component(
    "streamlit_deckgl", path=str(frontend_dir)
)

# Create the python function that will be called
def st_deckgl(
    deck: pdk.Deck,
    key: Optional[str] = "deck_gl",
    height: int = 500,
    events: Optional[list] = None,
    description: Optional[dict] = None,
    configuration: Optional[dict] = None,
    overlay: Optional[pdk.Layer] = None,
):
    """Create a deck.gl map in Streamlit.

    Parameters
    ==========
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
    overlay:pydeck.Layer instance, default None
        A second pydeck layer to overlay on the map - useful for land masks etc.
    configuration : dict, default None
        A dictionary of configuration options for the map.

    Returns
    =======
    component_value : dict
        A dictionary containing the info dictionary of the event.

    """
    json = deck.to_json()
    overlay_json = overlay.to_json() if overlay else None
    customLibraries = pdk.settings.custom_libraries
    configuration = pdk.settings.configuration

    mapbox_key = deck.mapbox_key or (overlay and overlay.mapbox_key)
    google_maps_key = deck.google_maps_key or (overlay and overlay.google_maps_key)

    component_value = _component_func(
        key=key,
        height=height,
        spec=json,
        tooltip=deck._tooltip,
        customLibraries=customLibraries,
        configuration=configuration,
        events=events,
        description=description,
        overlay=overlay_json,
        mapbox_key=mapbox_key,
        google_maps_key=google_maps_key,
    )

    return component_value
