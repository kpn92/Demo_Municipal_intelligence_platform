import { ROAD_LAYER_STYLES, LAND_USE_PALETTE, URBAN_UNIT_PALETTE, CLEANING_AREA_PALETTE } from "./layerDefinitions.js";

export function getContextFillColor(layerId, geojson) {
  const colors = {
    cleaning_areas: "#34d399", land_use_zones: "#f59e0b", line_roads: "#4b5f79",
    municipality_boundary: "#7dd3fc", polygon_roads: "#ef4444", unassigned_areas: "#64748b",
    assigned_areas: "#f0b84b", active_areas: "#f59e0b", completed_areas: "#22c55e",
    incomplete_areas: "#b45f45", selected_area_highlight: "#22c55e",
  };
  if (layerId === "cleaning_areas2") return getCleaningAreaColorExpression(geojson);
  if (layerId === "urban_units") return getUrbanUnitColorExpression(geojson);
  if (layerId === "land_use_zones") return getLandUseColorExpression(geojson);
  return colors[layerId] || "#64748b";
}

export function getContextLineColor(layerId) {
  if (layerId === "priority_roads") return ["case", ["<=", ["to-number", ["get", "priority"]], 0], "#ef4444", "#f97316"];
  if (ROAD_LAYER_STYLES[layerId]?.lineColor) return ROAD_LAYER_STYLES[layerId].lineColor;
  const colors = {
    cleaning_areas: "#8df0c2", cleaning_areas2: "#e6f1f8", land_use_zones: "#facc15",
    line_roads: "#5b7089", municipality_boundary: "#bfe8fb", polygon_roads: "#fecaca",
    unassigned_areas: "#94a3b8", assigned_areas: "#ffd166", active_areas: "#fbbf24",
    completed_areas: "#86efac", incomplete_areas: "#e18a6c", selected_area_highlight: "#f2c66d",
    selected_zone_roads: "#c6f1fb", manual_selected_roads: "#ffd166", hover_road: "#fff7ad",
    assigned_roads: "#8ed0ff", active_roads: "#f59e0b", pending_roads: "#ef4444",
    completed_roads: "#b9f3d3", urban_units: "#dcecf5",
  };
  return colors[layerId] || "#cbd5e1";
}

export function getContextFillOpacity(layerId) {
  const opacities = {
    cleaning_areas: 0.16, cleaning_areas2: 0.28, land_use_zones: 0.42, line_roads: 0,
    municipality_boundary: 0.045, polygon_roads: 0.68, unassigned_areas: 0.08, assigned_areas: 0.18,
    active_areas: 0.22, completed_areas: 0.18, incomplete_areas: 0.22, selected_area_highlight: 0.045, urban_units: 0.18,
  };
  return opacities[layerId] ?? 0.04;
}

export function getContextLineWidth(layerId) {
  const widths = {
    cleaning_areas: 2, cleaning_areas2: 1.5, land_use_zones: 2.1, line_roads: 2.6,
    municipality_boundary: 2.6, polygon_roads: 2.2, unassigned_areas: 1.2, assigned_areas: 2.4,
    active_areas: 2.4, completed_areas: 2.2, incomplete_areas: 2.4, selected_area_highlight: 1.9,
    selected_zone_roads: 2.3, manual_selected_roads: 3.2, hover_road: 5.2, assigned_roads: 3,
    active_roads: 3.2, pending_roads: 3.2, priority_roads: 3.2, completed_roads: 2.8, urban_units: 1.2,
  };
  return widths[layerId] ?? 2.4;
}

export function getContextLineOpacity(layerId) {
  if (ROAD_LAYER_STYLES[layerId]?.lineOpacity !== undefined) return ROAD_LAYER_STYLES[layerId].lineOpacity;
  const opacities = {
    cleaning_areas: 0.9, cleaning_areas2: 0.88, land_use_zones: 0.95, line_roads: 0.28,
    municipality_boundary: 1, polygon_roads: 1, unassigned_areas: 0.7, assigned_areas: 0.96,
    active_areas: 0.94, completed_areas: 0.92, incomplete_areas: 0.94, selected_area_highlight: 0.82,
    selected_zone_roads: 0.72, manual_selected_roads: 0.98, hover_road: 1, assigned_roads: 0.94,
    priority_roads: 0.9, completed_roads: 0.82, urban_units: 0.85,
  };
  return opacities[layerId] ?? 0.72;
}

export function getRoadLineWidth(layerId) {
  return ROAD_LAYER_STYLES[layerId]?.lineWidth || ["interpolate", ["linear"], ["zoom"], 12, 1.2, 14, 2.2, 16, 3.8];
}
export function getRoadHitWidth(layerId) {
  return ROAD_LAYER_STYLES[layerId]?.hitWidth || ["interpolate", ["linear"], ["zoom"], 12, 14, 14, 20, 16, 28];
}
export function getRoadCasingWidth(layerId) {
  return ROAD_LAYER_STYLES[layerId]?.casingWidth || ["interpolate", ["linear"], ["zoom"], 12, 2.8, 14, 4.8, 16, 6.4];
}
export function getRoadCasingColor(layerId) {
  return ROAD_LAYER_STYLES[layerId]?.casingColor || "rgba(7, 15, 26, 0.92)";
}
export function getRoadCasingOpacity(layerId) {
  return ROAD_LAYER_STYLES[layerId]?.casingOpacity ?? 0.92;
}

function getUrbanUnitColorExpression(geojson) {
  const expression = ["match", ["to-number", ["get", "gid"]]];
  (geojson?.features || []).forEach((feature, index) => {
    const gid = Number(feature?.properties?.gid);
    if (!Number.isFinite(gid)) return;
    expression.push(gid, URBAN_UNIT_PALETTE[index % URBAN_UNIT_PALETTE.length]);
  });
  expression.push("#38bdf8");
  return expression;
}

function getCleaningAreaColorExpression(geojson) {
  const expression = ["match", ["get", "area_code"]];
  (geojson?.features || []).forEach((feature, index) => {
    const code = String(feature?.properties?.area_code || feature?.properties?.name || "");
    if (!code) return;
    expression.push(code, CLEANING_AREA_PALETTE[index % CLEANING_AREA_PALETTE.length]);
  });
  expression.push("#22c55e");
  return expression;
}

function getLandUseColorExpression(geojson) {
  const expression = ["match", ["get", "onomasia"]];
  const seen = new Set();
  (geojson?.features || []).forEach((feature) => {
    const name = String(feature?.properties?.onomasia || "").trim();
    if (!name || seen.has(name)) return;
    seen.add(name);
    expression.push(name, getLandUseColor(name));
  });
  expression.push(LAND_USE_PALETTE.default);
  return expression;
}

function getLandUseColor(name) {
  const v = name.toLocaleUpperCase("el-GR");
  if (v.includes("ΠΡΑΣΙΝ") || v.includes("ΠΛΑΤΕΙΑ") || v.includes("ΕΛΕΥΘΕΡΟΙ ΧΩΡΟΙ")) return LAND_USE_PALETTE.green;
  if (v.includes("ΓΕΝΙΚΗ ΚΑΤΟΙΚΙΑ Α")) return LAND_USE_PALETTE.housingA;
  if (v.includes("ΓΕΝΙΚΗ ΚΑΤΟΙΚΙΑ Β")) return LAND_USE_PALETTE.housingB;
  if (v.includes("ΕΚΠΑΙΔΕΥ")) return LAND_USE_PALETTE.education;
  if (v.includes("ΑΘΛΗΤ")) return LAND_USE_PALETTE.sports;
  if (v.includes("ΠΟΛΙΤΙΣ")) return LAND_USE_PALETTE.culture;
  if (v.includes("ΚΕΝΤΡΟ") || v.includes("ΚΕΝΤΡΙΚ")) return LAND_USE_PALETTE.center;
  if (v.includes("ΒΙΟΜ") || v.includes("ΒΙΠΑ") || v.includes("ΠΑΡΑΓΩΓΙΚ")) return LAND_USE_PALETTE.industry;
  if (v.includes("ΛΙΜ") || v.includes("ΟΛΠ")) return LAND_USE_PALETTE.port;
  if (v.includes("ΕΙΔΙΚ") || v.includes("ΖΩΝΗ")) return LAND_USE_PALETTE.special;
  if (v.includes("ΔΙΟΙΚ")) return LAND_USE_PALETTE.administration;
  if (v.includes("ΝΕΚΡΟΤΑΦ")) return LAND_USE_PALETTE.cemetery;
  if (v.includes("ΑΡΧΑΙΟΛ")) return LAND_USE_PALETTE.archaeology;
  if (v.includes("ΔΕΗ") || v.includes("ΔΕΠΑ") || v.includes("ΕΥΔΑΠ")) return LAND_USE_PALETTE.utilities;
  return LAND_USE_PALETTE.default;
}
