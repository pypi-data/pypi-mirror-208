const { DeckGL, JSONConverter, carto } = deck;

/**
 * The component's render function. This will be called immediately after
 * the component is initially loaded, and then again every time the
 * component gets new data from Python.
 */

function onRender(event) {
  // Only run the render code the first time the component is loaded.
  if (!window.rendered) {
    const {
      spec,
      tooltip,
      height,
      customLibraries,
      configuration,
      decription,
      events,
      description,
      overlay,
      mapbox_key,
      google_maps_key,
    } = event.detail.args;

    const eventlist = events && events.map((event) => `deck-${event}-event`);

    const container = document.getElementById("deckgl-primary");
    container.style.width = window.innerWidth - 10 + "px";
    container.style.height = height - 10 + "px";
    container.style.position = "absolute";
    const ocontainer = document.getElementById("deckgl-overlay");
    ocontainer.style.width = window.innerWidth - 10 + "px";
    ocontainer.style.height = height - 10 + "px";
    ocontainer.style.position = "absolute";
    ocontainer.style["pointer-events"] = "none";

    const mapSpec = JSON.parse(spec);

    let deckInstance = null;
    let overlayInstance = null;

    const mapEventHandler = (eventType, info) => {
      if (eventType === "deck-view-state-change-event") {
        currentViewState = info;
        console.log(info);

        if (overlayInstance) {
          overlayInstance.setProps({ viewState: currentViewState });
        }
      }

      if (events && eventlist.includes(eventType) && info.object) {
        Streamlit.setComponentValue(info.object);
      }
    };

    deckInstance = createDeck({
      mapboxApiKey: mapbox_key,
      googleMapsApiKey: google_maps_key,
      container,
      jsonInput: mapSpec,
      tooltip,
      customLibraries,
      configuration,
      handleEvent: mapEventHandler,
    });

    if (overlay) {
      const overlaySpec = JSON.parse(overlay);
      overlaySpec.viewState = mapSpec.initialViewState || {};
      overlaySpec.style = {
        ...overlaySpec.style,
        "z-index": 1,
        "pointer-events": "none",
      };
      overlaySpec.views[0].controller = false;
      overlayInstance = createDeck({
        mapboxApiKey: mapbox_key,
        googleMapsApiKey: google_maps_key,
        container: ocontainer,
        jsonInput: overlaySpec,
        tooltip,
        customLibraries,
        configuration,
      });
    }

    if (description) {
      for (const key in description) {
        if (
          ["top-right", "top-left", "bottom-right", "bottom-left"].includes(key)
        ) {
          const pos = key.split("-");
          const style = `z-index:10; position: absolute; ${pos[0]}:10px; ${pos[1]}:10px;`;
          const div = document.createElement("div");
          div.innerHTML = description[key];
          div.style = style;
          container.appendChild(div);
        }
      }
    }

    Streamlit.setFrameHeight(height);
    window.rendered = true;
  }
}

// Render the component whenever python send a "render event"
Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender);
// Tell Streamlit that the component is ready to receive events
Streamlit.setComponentReady();
// Render with the correct height, if this is a fixed-height component
