import { useState, useCallback } from "react";
import { normalizeSearchText } from "../../../shared/lib/formatters.js";
import useOperationsStore from "../../../store/useOperationsStore.js";

export function useMapSearch(whenReady) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [activeId, setActiveId] = useState(null);

  const gisLayerCache = useOperationsStore((s) => s.gisLayerCache);

  const search = useCallback(
    (value) => {
      setQuery(value);
      if (!value.trim()) {
        setResults([]);
        return;
      }
      const q = normalizeSearchText(value);
      const roads = gisLayerCache["line_roads"]?.features || [];
      const hits = roads
        .filter((f) => {
          const name = normalizeSearchText(
            f.properties?.name || f.properties?.ref || f.properties?.road_name || ""
          );
          return name.includes(q);
        })
        .slice(0, 12)
        .map((f) => ({
          id: f.properties?.id ?? f.properties?.road_id,
          label: f.properties?.name || f.properties?.ref || f.properties?.road_name || "–",
        }));
      setResults(hits);
    },
    [gisLayerCache]
  );

  const flyTo = useCallback(
    (result) => {
      setActiveId(result.id);
      setQuery(result.label);
      setResults([]);

      const roads = gisLayerCache["line_roads"]?.features || [];
      const feature = roads.find(
        (f) => (f.properties?.id ?? f.properties?.road_id) === result.id
      );
      if (!feature) return;

      const coords = extractCoords(feature.geometry);
      if (!coords.length) return;

      const lon = coords.reduce((s, c) => s + c[0], 0) / coords.length;
      const lat = coords.reduce((s, c) => s + c[1], 0) / coords.length;

      whenReady((map) => map.easeTo({ center: [lon, lat], zoom: Math.max(map.getZoom(), 15), duration: 600 }));
    },
    [gisLayerCache, whenReady]
  );

  const clear = useCallback(() => {
    setQuery("");
    setResults([]);
    setActiveId(null);
  }, []);

  return { query, results, activeId, search, flyTo, clear };
}

function extractCoords(geometry) {
  if (!geometry) return [];
  if (geometry.type === "LineString") return geometry.coordinates;
  if (geometry.type === "MultiLineString") return geometry.coordinates.flat();
  return [];
}
