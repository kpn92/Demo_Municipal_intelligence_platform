import { useEffect, useRef } from "react";
import useOperationsStore from "../../../store/useOperationsStore.js";
import { bringContextLayersToFront } from "../lib/renderers.js";
import {
  COLLECTION_BINS_CLUSTER_OPTIONS,
  COLLECTION_BIN_LAYER_IDS,
  makeCollectionBinsHeatmapLayer,
  makeCollectionBinsClusterLayer,
  makeCollectionBinsClusterLabelLayer,
  makeCollectionBinsUnclusteredLayer,
  makeCollectionBinsFillBarLayer,
} from "../lib/layerDefinitions.js";

const BINS_SOURCE = "fleet-area-bins";
const HEAT_SOURCE = "fleet-area-bins-heat";
const HL_SOURCE   = "fleet-area-highlight";
const CONTEXT_VERSION = "20260505-01";

const ALL_BIN_LAYER_IDS = Object.values(COLLECTION_BIN_LAYER_IDS);
const OLD_BIN_LAYER_IDS = [`${BINS_SOURCE}-circle`, `${BINS_SOURCE}-label`, "bin-labels"];

const INDIVIDUAL_LAYERS = [
  COLLECTION_BIN_LAYER_IDS.clusters,
  COLLECTION_BIN_LAYER_IDS.clusterLabels,
  COLLECTION_BIN_LAYER_IDS.unclustered,
  COLLECTION_BIN_LAYER_IDS.fillBar,
];

// ── Helpers ───────────────────────────────────────────────────────────────────

function binsToGeojson(bins) {
  return {
    type: "FeatureCollection",
    features: bins
      .filter((b) => b.location)
      .map((b) => ({
        type: "Feature",
        geometry: { type: "Point", coordinates: [b.location.lng, b.location.lat] },
        properties: {
          id:         b.id,
          bin_code:   b.bin_code,
          status:     b.status,
          fill_level: b.fill_level ?? 0,
          area_code:  b.area_code,
        },
      })),
  };
}

function bboxFromBins(bins) {
  let minLng = Infinity, minLat = Infinity, maxLng = -Infinity, maxLat = -Infinity;
  for (const b of bins) {
    if (!b.location) continue;
    const { lng, lat } = b.location;
    if (lng < minLng) minLng = lng;
    if (lng > maxLng) maxLng = lng;
    if (lat < minLat) minLat = lat;
    if (lat > maxLat) maxLat = lat;
  }
  return isFinite(minLng) ? [[minLng, minLat], [maxLng, maxLat]] : null;
}

function normalize(s) {
  return (s ?? "").toUpperCase().replace(/\s+/g, " ").trim();
}

function layerVis(map, id, visible) {
  if (map.getLayer(id)) map.setLayoutProperty(id, "visibility", visible ? "visible" : "none");
}

function removeLayerSafe(map, id) { if (map.getLayer(id)) map.removeLayer(id); }
function removeSourceSafe(map, id) { if (map.getSource(id)) map.removeSource(id); }

function removeBinsLayers(map) {
  ALL_BIN_LAYER_IDS.forEach((id) => removeLayerSafe(map, id));
  OLD_BIN_LAYER_IDS.forEach((id) => removeLayerSafe(map, id));
  removeSourceSafe(map, BINS_SOURCE);
  removeSourceSafe(map, HEAT_SOURCE);
}

function removeHlLayers(map) {
  removeLayerSafe(map, `${HL_SOURCE}-fill`);
  removeLayerSafe(map, `${HL_SOURCE}-outline`);
  removeSourceSafe(map, HL_SOURCE);
}

function applyBinVisibility(map, individualMode) {
  // Heatmap: visible when Κάδοι pill OFF; hidden when pill ON
  layerVis(map, COLLECTION_BIN_LAYER_IDS.heatmap, !individualMode);
  // Individual layers: visible when pill ON
  INDIVIDUAL_LAYERS.forEach((id) => layerVis(map, id, individualMode));
}

// ── Hook ──────────────────────────────────────────────────────────────────────

export function useFleetMap(whenReady) {
  const currentView       = useOperationsStore((s) => s.currentView);
  const selectedFleetArea = useOperationsStore((s) => s.selectedFleetArea);
  const allFleetBins      = useOperationsStore((s) => s.allFleetBins);
  const visibleContextLayers = useOperationsStore((s) => s.visibleContextLayers);
  const urbanUnitsRef     = useRef(null);
  const clickBoundRef     = useRef(false);

  const individualMode = visibleContextLayers.has("fleet_bins");

  // Pre-fetch urban_units once for area highlight polygon
  useEffect(() => {
    if (urbanUnitsRef.current) return;
    fetch(`/context/urban_units.geojson?v=${CONTEXT_VERSION}`)
      .then((r) => r.json())
      .then((data) => { urbanUnitsRef.current = data; })
      .catch(() => {});
  }, []);

  // Bind cluster click once — zoom in +3
  useEffect(() => {
    if (clickBoundRef.current) return;
    whenReady((map) => {
      if (clickBoundRef.current) return;
      clickBoundRef.current = true;
      map.on("click", COLLECTION_BIN_LAYER_IDS.clusters, (e) => {
        const f = e.features?.[0];
        if (!f) return;
        map.flyTo({ center: f.geometry.coordinates, zoom: Math.min(map.getZoom() + 3, 19), duration: 700 });
      });
      map.on("mouseenter", COLLECTION_BIN_LAYER_IDS.clusters, () => { map.getCanvas().style.cursor = "pointer"; });
      map.on("mouseleave", COLLECTION_BIN_LAYER_IDS.clusters, () => { map.getCanvas().style.cursor = ""; });
    });
  }, [whenReady]);

  // Single effect handles EVERYTHING: layer setup, data updates, visibility toggle.
  // Source-based check (map.getSource) instead of layer-based — more reliable.
  useEffect(() => {
    // ── Cleanup when leaving fleet view ──────────────────────────────────────
    if (currentView !== "fleet") {
      whenReady((map) => { removeBinsLayers(map); removeHlLayers(map); });
      return;
    }

    // ── Wait for bin data ─────────────────────────────────────────────────────
    const bins = selectedFleetArea ? selectedFleetArea.bins : allFleetBins;
    console.log("[FleetMap] effect fired", { currentView, binsLen: bins.length, individualMode, hasFleetBins: visibleContextLayers.has("fleet_bins") });
    if (bins.length === 0) return;

    const geojson = binsToGeojson(bins);
    const bbox    = selectedFleetArea ? bboxFromBins(selectedFleetArea.bins) : null;

    const getHlGeojson = () => {
      if (!selectedFleetArea) return { type: "FeatureCollection", features: [] };
      const match = urbanUnitsRef.current?.features.find(
        (f) => normalize(f.properties.perigrafi) === normalize(selectedFleetArea.area_name)
      ) ?? null;
      return { type: "FeatureCollection", features: match ? [match] : [] };
    };

    whenReady((map) => {
      const sourcesExist = !!map.getSource(HEAT_SOURCE);
      console.log("[FleetMap] whenReady", { sourcesExist, individualMode });
      // ── Bins: create sources+layers once, update data on subsequent calls ──
      if (sourcesExist) {
        // Sources exist — just push new data
        map.getSource(HEAT_SOURCE).setData(geojson);
        map.getSource(BINS_SOURCE).setData(geojson);
      } else {
        // First time (or after leaving fleet) — build everything fresh
        removeBinsLayers(map); // clear any leftover old layers
        map.addSource(HEAT_SOURCE, { type: "geojson", data: geojson });
        map.addSource(BINS_SOURCE, { type: "geojson", data: geojson, ...COLLECTION_BINS_CLUSTER_OPTIONS });
        map.addLayer(makeCollectionBinsHeatmapLayer(HEAT_SOURCE));
        map.addLayer(makeCollectionBinsClusterLayer(BINS_SOURCE));
        map.addLayer(makeCollectionBinsClusterLabelLayer(BINS_SOURCE));
        map.addLayer(makeCollectionBinsUnclusteredLayer(BINS_SOURCE));
        map.addLayer(makeCollectionBinsFillBarLayer(BINS_SOURCE));
      }

      // Always apply visibility after every state change
      console.log("[FleetMap] calling applyBinVisibility", { individualMode });
      applyBinVisibility(map, individualMode);

      // ── Highlight selected area ───────────────────────────────────────────
      const hlGeojson = getHlGeojson();
      const showHl    = selectedFleetArea !== null;
      const hlSrc     = map.getSource(HL_SOURCE);
      if (hlSrc) {
        hlSrc.setData(hlGeojson);
        layerVis(map, `${HL_SOURCE}-fill`,    showHl);
        layerVis(map, `${HL_SOURCE}-outline`, showHl);
      } else {
        map.addSource(HL_SOURCE, { type: "geojson", data: hlGeojson });
        map.addLayer({ id: `${HL_SOURCE}-fill`,    type: "fill", source: HL_SOURCE, paint: { "fill-color": "#36c2d4", "fill-opacity": 0.12 } });
        map.addLayer({ id: `${HL_SOURCE}-outline`, type: "line", source: HL_SOURCE, paint: { "line-color": "#36c2d4", "line-width": 2.5, "line-dasharray": [2, 1.2] } });
        if (!showHl) {
          layerVis(map, `${HL_SOURCE}-fill`,    false);
          layerVis(map, `${HL_SOURCE}-outline`, false);
        }
      }

      bringContextLayersToFront(map);

      if (bbox && selectedFleetArea) {
        map.fitBounds(bbox, { padding: 100, duration: 800, maxZoom: 16 });
      }
    });
  }, [currentView, selectedFleetArea, allFleetBins, individualMode, whenReady]);
}
