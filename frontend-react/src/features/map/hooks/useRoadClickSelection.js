import { useEffect, useRef } from "react";
import useAssignmentStore from "../../../store/useAssignmentStore.js";

const HIT_LAYERS = [
  "context-line_roads-hit",
  "context-selected_zone_roads-hit",
  "context-line_roads-line",
  "context-selected_zone_roads-line",
];

function getSegmentCode(props) {
  return String(props?.segment_code || props?.road_id || props?.id || "");
}

export function useRoadClickSelection(whenReady) {
  const roadClickActive = useAssignmentStore((s) => s.roadClickActive);
  const mapRef = useRef(null);

  useEffect(() => {
    whenReady((m) => { mapRef.current = m; });
  }, [whenReady]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;

    if (!roadClickActive) {
      map.getCanvas().style.cursor = "";
      return;
    }

    map.getCanvas().style.cursor = "crosshair";

    const handler = (e) => {
      const available = HIT_LAYERS.filter((id) => { try { return map.getLayer(id); } catch { return false; } });
      if (!available.length) return;
      const features = map.queryRenderedFeatures(e.point, { layers: available });
      if (!features.length) return;
      const code = getSegmentCode(features[0].properties);
      if (code) useAssignmentStore.getState().toggleRoadCode(code);
    };

    map.on("click", handler);
    return () => {
      map.off("click", handler);
      map.getCanvas().style.cursor = "";
    };
  }, [roadClickActive]);
}
