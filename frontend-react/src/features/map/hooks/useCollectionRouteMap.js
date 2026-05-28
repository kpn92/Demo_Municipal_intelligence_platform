import { useEffect } from "react";
import maplibregl from "maplibre-gl";
import useOperationsStore from "../../../store/useOperationsStore.js";

const ROUTE_SOURCE = "collection-route";
const ROUTE_LAYER = "collection-route-line";

// Module-level marker ref so the animation loop can move it without prop drilling
let _collectionMarker = null;

export function updateCollectionMarkerPosition(pos) {
  _collectionMarker?.setLngLat(pos);
}

export function removeCollectionMarker() {
  _collectionMarker?.remove();
  _collectionMarker = null;
}

function createTruckEl() {
  const el = document.createElement("div");
  el.className = "collection-anim-marker";
  el.innerHTML = `<svg viewBox="0 0 32 24" width="32" height="24">
    <rect x="1" y="6" width="22" height="14" rx="2" fill="#36c2d4" stroke="#0c0f17" stroke-width="1.5"/>
    <rect x="23" y="10" width="8" height="8" rx="1" fill="#36c2d4" stroke="#0c0f17" stroke-width="1.5"/>
    <circle cx="7" cy="21" r="3" fill="#0c0f17" stroke="#36c2d4" stroke-width="1.5"/>
    <circle cx="19" cy="21" r="3" fill="#0c0f17" stroke="#36c2d4" stroke-width="1.5"/>
    <circle cx="27" cy="21" r="2.5" fill="#0c0f17" stroke="#36c2d4" stroke-width="1.5"/>
  </svg>`;
  return el;
}

function routeToGeojson(allBins) {
  const coords = allBins
    .filter((b) => b.location)
    .map((b) => [Number(b.location.lng), Number(b.location.lat)]);
  return {
    type: "FeatureCollection",
    features: coords.length > 1
      ? [{ type: "Feature", geometry: { type: "LineString", coordinates: coords }, properties: {} }]
      : [],
  };
}

export function useCollectionRouteMap(whenReady) {
  const route = useOperationsStore((s) => s.collectionWizard.route);
  const currentView = useOperationsStore((s) => s.currentView);
  const fleetSubTab = useOperationsStore((s) => s.fleetSubTab);

  useEffect(() => {
    const isAssignment = currentView === "fleet" && fleetSubTab === "assignment";

    whenReady((map) => {
      // Remove existing route layer
      if (map.getLayer(ROUTE_LAYER)) map.removeLayer(ROUTE_LAYER);
      if (map.getSource(ROUTE_SOURCE)) map.removeSource(ROUTE_SOURCE);

      // Remove truck marker
      removeCollectionMarker();

      if (!isAssignment || !route?.allBins?.length) return;

      // Add route line
      const geojson = routeToGeojson(route.allBins);
      map.addSource(ROUTE_SOURCE, { type: "geojson", data: geojson });
      map.addLayer({
        id: ROUTE_LAYER,
        type: "line",
        source: ROUTE_SOURCE,
        paint: {
          "line-color": "#36c2d4",
          "line-width": 2.5,
          "line-dasharray": [2, 1.5],
          "line-opacity": 0.7,
        },
      });

      // Fit map to route bounds
      const coords = route.allBins
        .filter((b) => b.location)
        .map((b) => [Number(b.location.lng), Number(b.location.lat)]);
      if (coords.length > 1) {
        const lngs = coords.map((c) => c[0]);
        const lats = coords.map((c) => c[1]);
        map.fitBounds(
          [[Math.min(...lngs), Math.min(...lats)], [Math.max(...lngs), Math.max(...lats)]],
          { padding: 80, duration: 800, maxZoom: 15 },
        );
      }

      // Create truck marker at start position
      const startPos = [
        Number(route.allBins[0].location.lng),
        Number(route.allBins[0].location.lat),
      ];
      _collectionMarker = new maplibregl.Marker({ element: createTruckEl(), anchor: "center" })
        .setLngLat(startPos)
        .addTo(map);
    });
  }, [route, currentView, fleetSubTab, whenReady]);
}
