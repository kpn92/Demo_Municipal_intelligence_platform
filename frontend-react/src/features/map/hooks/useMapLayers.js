import { useEffect, useRef } from "react";
import useOperationsStore from "../../../store/useOperationsStore.js";
import {
  applyContextLayer,
  removeContextLayer,
  applyBasemapBuildingsLayer,
  removeBasemapBuildingsLayer,
} from "../lib/renderers.js";

const CONTEXT_VERSION = "20260505-01";

async function loadContextLayer(layerId, cache) {
  if (cache[layerId]) return cache[layerId];
  const res = await fetch(`/context/${layerId}.geojson?v=${CONTEXT_VERSION}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export function useMapLayers(whenReady) {
  const prevRef = useRef(new Set());

  const visibleContextLayers = useOperationsStore((s) => s.visibleContextLayers);
  const setGisLayer = useOperationsStore((s) => s.setGisLayer);

  useEffect(() => {
    const prev = prevRef.current;
    const curr = visibleContextLayers;

    const toAdd = [...curr].filter((id) => !prev.has(id));
    const toRemove = [...prev].filter((id) => !curr.has(id));

    toRemove.forEach((layerId) => {
      if (layerId === "buildings_25d") {
        whenReady((map) => removeBasemapBuildingsLayer(map));
      } else if (layerId === "fleet_bins") {
        // "Κάδοι" OFF → heatmap visible, individual layers hidden
        // (useFleetMap handles this via visibleContextLayers subscription)
      } else {
        whenReady((map) => removeContextLayer(map, layerId));
      }
    });

    toAdd.forEach(async (layerId) => {
      if (layerId === "buildings_25d") {
        whenReady((map) => applyBasemapBuildingsLayer(map));
        return;
      }
      if (layerId === "fleet_bins") {
        // "Κάδοι" ON → individual layers visible, heatmap hidden
        // (useFleetMap handles this via visibleContextLayers subscription)
        return;
      }
      try {
        const geojson = await loadContextLayer(layerId, useOperationsStore.getState().gisLayerCache);
        setGisLayer(layerId, geojson);
        whenReady((map) => applyContextLayer(map, layerId, geojson));
      } catch (err) {
        console.warn(`[useMapLayers] Failed to load "${layerId}":`, err);
      }
    });

    prevRef.current = new Set(curr);
  }, [visibleContextLayers, whenReady, setGisLayer]);
}
