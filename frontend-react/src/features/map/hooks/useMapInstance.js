import { useEffect, useRef, useCallback } from "react";
import maplibregl from "maplibre-gl";
import { KERATSINI_MAP_VIEW, MAP_STYLE_URL } from "../lib/mapConfig.js";
import useOperationsStore from "../../../store/useOperationsStore.js";

export function useMapInstance(containerRef) {
  const mapRef = useRef(null);
  const readyRef = useRef(false);

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;

    const map = new maplibregl.Map({
      container: containerRef.current,
      style: MAP_STYLE_URL,
      center: KERATSINI_MAP_VIEW.center,
      zoom: KERATSINI_MAP_VIEW.zoom,
      pitch: KERATSINI_MAP_VIEW.pitch,
      bearing: KERATSINI_MAP_VIEW.bearing,
      attributionControl: false,
    });

    map.addControl(new maplibregl.NavigationControl({ visualizePitch: true }), "bottom-right");

    map.on("load", () => {
      readyRef.current = true;
      bindCompassToggle(map);
      useOperationsStore.getState().setMapBounds(map.getBounds());
    });

    map.on("moveend", () => {
      useOperationsStore.getState().setMapBounds(map.getBounds());
    });

    mapRef.current = map;

    return () => {
      map.remove();
      mapRef.current = null;
      readyRef.current = false;
    };
  }, [containerRef]);

  const whenReady = useCallback((fn) => {
    const map = mapRef.current;
    if (!map) return;
    if (readyRef.current) {
      fn(map);
    } else {
      map.once("load", () => fn(map));
    }
  }, []);

  return { mapRef, whenReady };
}

function bindCompassToggle(map) {
  const btn = map.getContainer()?.querySelector(".maplibregl-ctrl-compass");
  if (!(btn instanceof HTMLButtonElement) || btn.dataset.toggleBound === "true") return;
  btn.dataset.toggleBound = "true";
  btn.title = "Εναλλαγή κατακόρυφης / αρχικής γωνίας";
  btn.setAttribute("aria-label", "Εναλλαγή κατακόρυφης / αρχικής γωνίας");
  btn.addEventListener("click", (e) => {
    e.preventDefault();
    e.stopPropagation();
    const isTopDown = Math.abs(map.getPitch()) < 1 && Math.abs(map.getBearing()) < 1;
    map.easeTo({
      center: map.getCenter(),
      zoom: map.getZoom(),
      pitch: isTopDown ? KERATSINI_MAP_VIEW.pitch : 0,
      bearing: isTopDown ? KERATSINI_MAP_VIEW.bearing : 0,
      duration: 700,
    });
  }, true);
}
