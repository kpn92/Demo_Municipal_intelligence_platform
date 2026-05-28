import { useState, useCallback, useMemo } from "react";
import useAssignmentStore from "../../../store/useAssignmentStore.js";
import useOperationsStore from "../../../store/useOperationsStore.js";
import { assignmentsService } from "../services/assignmentsService.js";

function extractLineCoords(geometry) {
  if (!geometry) return [];
  if (geometry.type === "LineString") return geometry.coordinates;
  if (geometry.type === "MultiLineString") return geometry.coordinates.flat();
  return [];
}

function getRoadCode(feature) {
  const p = feature.properties || {};
  return String(p.segment_code || p.road_id || p.id || "");
}

function boundsContainsAnyCoord(bounds, coords) {
  if (!bounds) return false;
  const w = bounds.getWest(), e = bounds.getEast(), s = bounds.getSouth(), n = bounds.getNorth();
  return coords.some(([lng, lat]) => lng >= w && lng <= e && lat >= s && lat <= n);
}

function getFeatureBBox(feature) {
  if (!feature?.geometry) return null;
  const coords = [];
  collectCoords(feature.geometry, coords);
  if (!coords.length) return null;
  const lons = coords.map((c) => c[0]);
  const lats = coords.map((c) => c[1]);
  return [[Math.min(...lons), Math.min(...lats)], [Math.max(...lons), Math.max(...lats)]];
}

function collectCoords(geometry, out) {
  if (!geometry) return;
  const { type, coordinates } = geometry;
  if (type === "Point") { out.push(coordinates); return; }
  if (type === "LineString" || type === "MultiPoint") { coordinates.forEach((c) => out.push(c)); return; }
  if (type === "Polygon" || type === "MultiLineString") { coordinates.forEach((ring) => ring.forEach((c) => out.push(c))); return; }
  if (type === "MultiPolygon") { coordinates.forEach((poly) => poly.forEach((ring) => ring.forEach((c) => out.push(c)))); return; }
  if (type === "GeometryCollection") { geometry.geometries.forEach((g) => collectCoords(g, out)); }
}

export function useAssignmentWizard(onComplete) {
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const planDate = useOperationsStore((s) => s.planDate);
  const employees = useOperationsStore((s) => s.employees);
  const gisLayerCache = useOperationsStore((s) => s.gisLayerCache);
  const pendingRoads = useOperationsStore((s) => s.pendingRoads);
  const setMapFitRequest = useOperationsStore((s) => s.setMapFitRequest);

  const {
    wizardStep, selectedAreaCode, selectedRoadCodes, selectedGroup, selectedEmployeeIds, assignmentPriority,
    roadClickActive,
    setWizardStep, setSelectedAreaCode, setSelectedGroup, setAssignmentPriority,
    toggleEmployee, cancelPlanning,
    setRoadClickActive, setSelectedRoadCodes, clearRoadCodes,
  } = useAssignmentStore();

  const cleaningAreas = gisLayerCache["cleaning_areas2"]?.features || gisLayerCache["cleaning_areas"]?.features || [];
  const lineRoads = gisLayerCache["line_roads"]?.features || [];

  const selectedAreaFeature = useMemo(
    () => cleaningAreas.find((f) => {
      const props = f.properties || {};
      const code = String(props.area_code || props.gid || props.onoma || "");
      return code === selectedAreaCode;
    }),
    [cleaningAreas, selectedAreaCode]
  );

  const areaRoads = selectedAreaCode
    ? lineRoads.filter((f) => {
        const p = f.properties || {};
        return String(p.area_code || "") === selectedAreaCode || String(p.gid || "") === selectedAreaCode;
      })
    : [];

  const selectedRoadFeatures = areaRoads.length
    ? (selectedRoadCodes.size ? areaRoads.filter((f) => selectedRoadCodes.has(String(f.properties?.segment_code || f.properties?.road_id || f.properties?.id || ""))) : areaRoads)
    : [];

  const canGoNext = useCallback(() => {
    if (wizardStep === 1) return Boolean(selectedAreaCode);
    if (wizardStep === 2) return true;
    if (wizardStep === 3) return Boolean(selectedGroup) && selectedEmployeeIds.size > 0;
    return true;
  }, [wizardStep, selectedAreaCode, selectedGroup, selectedEmployeeIds]);

  const next = useCallback(() => {
    if (wizardStep < 4 && canGoNext()) {
      const nextStep = wizardStep + 1;
      setWizardStep(nextStep);
      if (nextStep === 2 && selectedAreaFeature) {
        const bbox = getFeatureBBox(selectedAreaFeature);
        if (bbox) setMapFitRequest(bbox);
      }
    }
  }, [wizardStep, canGoNext, setWizardStep, selectedAreaFeature, setMapFitRequest]);

  const prev = useCallback(() => {
    if (wizardStep > 1) setWizardStep(wizardStep - 1);
  }, [wizardStep, setWizardStep]);

  const submit = useCallback(async () => {
    if (submitting) return;
    setError(null);
    setSubmitting(true);

    try {
      const roadSegments = assignmentsService.buildRoadSegments(selectedRoadFeatures, assignmentPriority);
      if (!roadSegments.length) {
        setError("Δεν βρέθηκαν δρόμοι στην επιλεγμένη περιοχή.");
        return;
      }

      const areaName = selectedAreaFeature?.properties?.onoma || selectedAreaFeature?.properties?.perigrafi || selectedAreaCode;
      const payload = assignmentsService.buildPayload({
        planDate,
        selectedAreaCode,
        areaName,
        selectedGroup,
        selectedEmployeeIds,
        employees,
        roadSegments,
        priority: assignmentPriority,
      });

      const created = await assignmentsService.create(payload);
      // Backend READ returns employees[] (nested), not employee_ids
      const createdEmployees = created.employees || [];
      const normalized = {
        id: created.id,
        areaCode: String(created.area_code || selectedAreaCode),
        areaName: created.area_name || areaName,
        groupName: created.crew_label || selectedGroup,
        assignmentDate: String(created.assignment_date || planDate),
        status: created.status || "assigned",
        notes: created.notes || "",
        employeeIds: createdEmployees.length
          ? createdEmployees.map((e) => String(e.employee_id ?? e.employee?.id ?? "")).filter(Boolean)
          : [...selectedEmployeeIds],
        employeeNames: createdEmployees.length
          ? createdEmployees.map((e) => `${e.employee?.first_name || ""} ${e.employee?.last_name || ""}`.trim()).filter(Boolean)
          : employees.filter((e) => selectedEmployeeIds.has(String(e.id))).map((e) => `${e.first_name} ${e.last_name}`),
        requiredPersonnel: created.required_personnel || selectedEmployeeIds.size,
        estimatedLengthKm: Number(created.estimated_length_km || 0),
        estimatedDurationMin: created.estimated_duration_min || 0,
        roadSegments: created.road_segments || roadSegments,
      };
      const { areaAssignments, setAreaAssignments } = useOperationsStore.getState();
      setAreaAssignments([...areaAssignments, normalized]);
      cancelPlanning();
      onComplete?.();
    } catch (err) {
      setError(err?.response?.data?.detail || "Σφάλμα κατά την αποθήκευση ανάθεσης.");
    } finally {
      setSubmitting(false);
    }
  }, [submitting, selectedRoadFeatures, assignmentPriority, selectedAreaFeature, selectedAreaCode, planDate, selectedGroup, selectedEmployeeIds, employees, cancelPlanning, onComplete]);

  const selectAllRoads = useCallback(() => {
    const codes = areaRoads.map(getRoadCode).filter(Boolean);
    setSelectedRoadCodes(codes);
  }, [areaRoads, setSelectedRoadCodes]);

  const selectVisibleRoads = useCallback(() => {
    const bounds = useOperationsStore.getState().mapBounds;
    const codes = areaRoads
      .filter((f) => boundsContainsAnyCoord(bounds, extractLineCoords(f.geometry)))
      .map(getRoadCode)
      .filter(Boolean);
    const current = useAssignmentStore.getState().selectedRoadCodes;
    setSelectedRoadCodes([...new Set([...current, ...codes])]);
  }, [areaRoads, setSelectedRoadCodes]);

  const addPendingRoads = useCallback(() => {
    const areaCode = useAssignmentStore.getState().selectedAreaCode;
    const pending = pendingRoads.filter(
      (r) => String(r.area_code || r.areaCode || "") === String(areaCode || "")
    );
    const codes = pending.map((r) => String(r.roadCode || r.road_code || "")).filter(Boolean);
    const current = useAssignmentStore.getState().selectedRoadCodes;
    setSelectedRoadCodes([...new Set([...current, ...codes])]);
  }, [pendingRoads, setSelectedRoadCodes]);

  const clearRoads = useCallback(() => {
    clearRoadCodes();
    setRoadClickActive(false);
  }, [clearRoadCodes, setRoadClickActive]);

  const toggleRoadClick = useCallback(() => {
    setRoadClickActive(!roadClickActive);
  }, [roadClickActive, setRoadClickActive]);

  return {
    wizardStep, selectedAreaCode, selectedGroup, selectedEmployeeIds, assignmentPriority,
    roadClickActive,
    cleaningAreas, employees, areaRoads, selectedRoadFeatures,
    canGoNext, next, prev, submit, submitting, error,
    setSelectedAreaCode, setSelectedGroup, setAssignmentPriority, toggleEmployee,
    selectAllRoads, selectVisibleRoads, addPendingRoads, clearRoads, toggleRoadClick,
    cancel: cancelPlanning,
  };
}
