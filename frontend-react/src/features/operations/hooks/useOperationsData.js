import { useEffect, useCallback, useRef } from "react";
import useOperationsStore from "../../../store/useOperationsStore.js";
import { operationsService } from "../services/operationsService.js";

const CONTEXT_VERSION = "20260505-01";
const GIS_LAYERS_TO_PRELOAD = ["cleaning_areas2", "cleaning_areas", "line_roads"];

async function preloadGisLayers() {
  const cache = useOperationsStore.getState().gisLayerCache;
  const setGisLayer = useOperationsStore.getState().setGisLayer;
  await Promise.all(
    GIS_LAYERS_TO_PRELOAD.map(async (layerId) => {
      if (cache[layerId]) return;
      try {
        const res = await fetch(`/context/${layerId}.geojson?v=${CONTEXT_VERSION}`);
        if (!res.ok) return;
        const geojson = await res.json();
        setGisLayer(layerId, geojson);
      } catch {
        // non-fatal: layer pills can still load these later
      }
    })
  );
}

export function useOperationsData() {
  const planDate = useOperationsStore((s) => s.planDate);
  const setAssignments = useOperationsStore((s) => s.setAssignments);
  const setEmployees = useOperationsStore((s) => s.setEmployees);
  const setAreaAssignments = useOperationsStore((s) => s.setAreaAssignments);
  const setAllAreaAssignments = useOperationsStore((s) => s.setAllAreaAssignments);
  const loadingRef = useRef(false);
  const gisPreloadedRef = useRef(false);

  const load = useCallback(async (date) => {
    if (loadingRef.current) return;
    loadingRef.current = true;
    try {
      const data = await operationsService.loadPlanData(date);
      setAssignments(data.assignments);
      setEmployees(data.employees);
      setAreaAssignments(data.areaAssignments);
      setAllAreaAssignments(data.allAreaAssignments);
    } catch (err) {
      console.warn("[useOperationsData] load failed:", err);
    } finally {
      loadingRef.current = false;
    }
  }, [setAssignments, setEmployees, setAreaAssignments, setAllAreaAssignments]);

  // Pre-load GIS layers needed by the wizard (cleaning_areas, line_roads)
  useEffect(() => {
    if (gisPreloadedRef.current) return;
    gisPreloadedRef.current = true;
    preloadGisLayers();
  }, []);

  useEffect(() => {
    load(planDate);
  }, [planDate, load]);

  return { reload: () => load(planDate) };
}
