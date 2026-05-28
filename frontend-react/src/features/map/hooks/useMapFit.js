import { useEffect } from "react";
import useOperationsStore from "../../../store/useOperationsStore.js";

export function useMapFit(whenReady) {
  const mapFitRequest = useOperationsStore((s) => s.mapFitRequest);
  const setMapFitRequest = useOperationsStore((s) => s.setMapFitRequest);

  useEffect(() => {
    if (!mapFitRequest) return;
    whenReady((map) => {
      map.fitBounds(mapFitRequest, { padding: 100, duration: 800 });
    });
    setMapFitRequest(null);
  }, [mapFitRequest, whenReady, setMapFitRequest]);
}
