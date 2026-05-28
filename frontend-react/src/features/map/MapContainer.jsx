import { useRef, useCallback } from "react";
import { useMapInstance } from "./hooks/useMapInstance.js";
import { useMapLayers } from "./hooks/useMapLayers.js";
import { useMapFit } from "./hooks/useMapFit.js";
import { useFleetMap } from "./hooks/useFleetMap.js";
import { useCollectionRouteMap } from "./hooks/useCollectionRouteMap.js";
import { useRoadClickSelection } from "./hooks/useRoadClickSelection.js";
import MapLayerPills from "./components/MapLayerPills.jsx";
import MapLegend from "./components/MapLegend.jsx";
import MapSearch from "./components/MapSearch.jsx";
import { KERATSINI_MAP_VIEW } from "./lib/mapConfig.js";

function MapContainer({ children }) {
  const containerRef = useRef(null);
  const { whenReady } = useMapInstance(containerRef);
  useMapLayers(whenReady);
  useMapFit(whenReady);
  useFleetMap(whenReady);
  useCollectionRouteMap(whenReady);
  useRoadClickSelection(whenReady);

  const handleFitMap = useCallback(() => {
    whenReady((map) =>
      map.flyTo({
        center: KERATSINI_MAP_VIEW.center,
        zoom: KERATSINI_MAP_VIEW.zoom,
        pitch: KERATSINI_MAP_VIEW.pitch,
        bearing: KERATSINI_MAP_VIEW.bearing,
        duration: 800,
      })
    );
  }, [whenReady]);

  return (
    <div className="map-shell">
      <div ref={containerRef} className="map-container" />
      <div className="map-top-bar">
        <MapSearch whenReady={whenReady} />
        <button
          type="button"
          className="map-fit-btn"
          onClick={handleFitMap}
          title="Επαναφορά χάρτη"
          aria-label="Επαναφορά χάρτη"
        >
          ⊕
        </button>
      </div>
      <MapLayerPills />
      <MapLegend />
      {children}
    </div>
  );
}

export default MapContainer;
