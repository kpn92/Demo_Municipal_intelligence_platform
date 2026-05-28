export const ROAD_LAYER_STYLES = {
  line_roads: {
    legendLabel: "Οδικό δίκτυο",
    lineColor: "#5b7089",
    lineOpacity: 0.28,
    lineWidth: ["interpolate", ["linear"], ["zoom"], 12, 0.7, 14, 1.2, 16, 1.8],
    casingColor: "rgba(8, 13, 22, 0.72)",
    casingOpacity: 0.46,
    casingWidth: ["interpolate", ["linear"], ["zoom"], 12, 1.3, 14, 1.9, 16, 2.6],
    hitWidth: ["interpolate", ["linear"], ["zoom"], 12, 14, 14, 18, 16, 24],
    legendWidth: 2,
    legendOpacity: 0.74,
  },
  selected_zone_roads: {
    legendLabel: "Δρόμοι επιλεγμένης περιοχής",
    lineColor: "#c6f1fb",
    lineOpacity: 0.72,
    lineWidth: ["interpolate", ["linear"], ["zoom"], 12, 1.4, 14, 2.1, 16, 3.1],
    casingColor: "rgba(12, 31, 40, 0.78)",
    casingOpacity: 0.68,
    casingWidth: ["interpolate", ["linear"], ["zoom"], 12, 2, 14, 2.9, 16, 4],
    hitWidth: ["interpolate", ["linear"], ["zoom"], 12, 18, 14, 24, 16, 32],
    legendWidth: 3,
    legendGlow: true,
  },
  manual_selected_roads: {
    legendLabel: "Επιλεγμένοι δρόμοι",
    lineColor: "#ffd166",
    lineOpacity: 0.98,
    lineWidth: ["interpolate", ["linear"], ["zoom"], 12, 2.4, 14, 3.4, 16, 5.1],
    casingColor: "rgba(73, 34, 10, 0.9)",
    casingOpacity: 0.92,
    casingWidth: ["interpolate", ["linear"], ["zoom"], 12, 3.4, 14, 4.8, 16, 6.6],
    hitWidth: ["interpolate", ["linear"], ["zoom"], 12, 18, 14, 24, 16, 32],
    legendWidth: 5,
    legendGlow: true,
  },
  hover_road: {
    legendLabel: "Δρόμος σε στόχευση",
    lineColor: "#fff7ad",
    lineOpacity: 1,
    lineWidth: ["interpolate", ["linear"], ["zoom"], 12, 5.2, 14, 7.2, 16, 9.2],
    casingColor: "rgba(69, 35, 22, 0.92)",
    casingOpacity: 0.96,
    casingWidth: ["interpolate", ["linear"], ["zoom"], 12, 7.2, 14, 9.2, 16, 11.2],
  },
  assigned_roads: {
    legendLabel: "Προγραμματισμένος δρόμος",
    lineColor: "#ffd166",
    lineOpacity: 0.98,
    lineWidth: ["interpolate", ["linear"], ["zoom"], 12, 1.9, 14, 2.7, 16, 3.9],
    casingColor: "rgba(73, 34, 10, 0.88)",
    casingOpacity: 0.9,
    casingWidth: ["interpolate", ["linear"], ["zoom"], 12, 2.5, 14, 3.6, 16, 5],
    legendWidth: 4,
    legendGlow: true,
  },
  active_roads: {
    legendLabel: "Δρόμος σε εξέλιξη",
    lineColor: "#f59e0b",
    lineOpacity: 0.94,
    lineWidth: ["interpolate", ["linear"], ["zoom"], 12, 2.1, 14, 3, 16, 4.2],
    casingColor: "rgba(71, 42, 10, 0.88)",
    casingOpacity: 0.88,
    casingWidth: ["interpolate", ["linear"], ["zoom"], 12, 2.8, 14, 4, 16, 5.4],
    legendWidth: 4,
  },
  pending_roads: {
    legendLabel: "Εκκρεμής δρόμος",
    lineColor: "#ef4444",
    lineOpacity: 0.94,
    lineWidth: ["interpolate", ["linear"], ["zoom"], 12, 2.1, 14, 3, 16, 4.2],
    casingColor: "rgba(76, 17, 17, 0.9)",
    casingOpacity: 0.9,
    casingWidth: ["interpolate", ["linear"], ["zoom"], 12, 2.8, 14, 4, 16, 5.4],
    legendWidth: 4,
  },
  priority_roads: {
    legendLabel: "Ένδειξη προτεραιότητας",
    lineColor: "#f97316",
    lineOpacity: 0.96,
    lineWidth: ["interpolate", ["linear"], ["zoom"], 12, 1.6, 14, 2.3, 16, 3.3],
    casingColor: "rgba(76, 17, 17, 0.86)",
    casingOpacity: 0.88,
    casingWidth: ["interpolate", ["linear"], ["zoom"], 12, 2.3, 14, 3.2, 16, 4.4],
    legendWidth: 4,
  },
  completed_roads: {
    legendLabel: "Ολοκληρωμένος δρόμος",
    lineColor: "#b9f3d3",
    lineOpacity: 0.82,
    lineWidth: ["interpolate", ["linear"], ["zoom"], 12, 1.8, 14, 2.5, 16, 3.6],
    casingColor: "rgba(13, 42, 31, 0.84)",
    casingOpacity: 0.8,
    casingWidth: ["interpolate", ["linear"], ["zoom"], 12, 2.3, 14, 3.3, 16, 4.6],
    legendWidth: 4,
  },
};

export const AREA_STATUS_STYLES = {
  unassigned_areas: { fill: "#64748b", fillOpacity: 0.08, outline: "rgba(148, 163, 184, 0.78)", outlineWidth: 1.2, outlineOpacity: 0.7 },
  assigned_areas: { fill: "#f0b84b", fillOpacity: 0.18, outline: "#ffd166", outlineWidth: 2.4, outlineOpacity: 0.96 },
  active_areas: { fill: "#f59e0b", fillOpacity: 0.22, outline: "#fbbf24", outlineWidth: 2.4, outlineOpacity: 0.94 },
  completed_areas: { fill: "#22c55e", fillOpacity: 0.18, outline: "#86efac", outlineWidth: 2.2, outlineOpacity: 0.92 },
  incomplete_areas: { fill: "#b45f45", fillOpacity: 0.22, outline: "#e18a6c", outlineWidth: 2.4, outlineOpacity: 0.94 },
};

export const URBAN_UNIT_PALETTE = ["#22c55e","#38bdf8","#f59e0b","#a78bfa","#f97316","#14b8a6","#f43f5e","#60a5fa"];
export const CLEANING_AREA_PALETTE = ["#22c55e","#14b8a6","#38bdf8","#60a5fa","#818cf8","#a78bfa","#f472b6","#fb7185","#f97316","#f59e0b"];
export const LAND_USE_PALETTE = { green: "#22c55e", housingA: "#60a5fa", housingB: "#2563eb", education: "#f59e0b", sports: "#06b6d4", culture: "#a855f7", center: "#ef4444", industry: "#64748b", special: "#f97316", administration: "#14b8a6", port: "#0f766e", cemetery: "#78716c", archaeology: "#b45309", utilities: "#84cc16", default: "#eab308" };

const FLAT_FOOTPRINT_AREA_LIMIT = 5792.877427549999993;
const FLAT_FOOTPRINT_IDS = [258,353,788,1088,1395,1466,1525,2235,3555,4100,4428,6283,6792,7242,7243,10524,11217,11612,11662,12437,14859,15407,15556,15867,15887,15901,15917,15997,16268,16460,16672];
const EXTRUDED_FOOTPRINT_IDS = [4348];

export { FLAT_FOOTPRINT_AREA_LIMIT, FLAT_FOOTPRINT_IDS, EXTRUDED_FOOTPRINT_IDS };

export const FLEET_BINS_SOURCE_OPTIONS = {
  cluster: true,
  clusterMaxZoom: 16,
  clusterRadius: 60,
  clusterProperties: {
    max_fill:     ["max", ["get", "fill_level"]],
    count_red:    ["+", ["case", [">=", ["to-number", ["get", "fill_level"]], 75], 1, 0]],
    count_orange: ["+", ["case", ["all", [">=", ["to-number", ["get", "fill_level"]], 50], ["<", ["to-number", ["get", "fill_level"]], 75]], 1, 0]],
  },
};

// ── Collection bins clustering (Module 1B — useFleetMap) ─────────────────────

export const COLLECTION_BINS_CLUSTER_OPTIONS = {
  cluster: true,
  clusterMaxZoom: 16,
  clusterRadius: 60,
  clusterProperties: {
    // count of bins with fill_level >= 70 (needs collection / full)
    count_full: ["+", ["case", [">=", ["to-number", ["get", "fill_level"]], 70], 1, 0]],
  },
};

// Cluster fill color: red if >30% full, amber if 10–30%, green if <10%
const CLUSTER_COLOR = [
  "case",
  [">", ["/", ["get", "count_full"], ["get", "point_count"]], 0.3], "#ef4444",
  [">", ["/", ["get", "count_full"], ["get", "point_count"]], 0.1], "#f59e0b",
  "#22c55e",
];

// Radius: larger below zoom 13 (neighbourhood), smaller 13–16 (block)
const CLUSTER_RADIUS = ["step", ["zoom"], 32, 13, 20];

export const COLLECTION_BIN_LAYER_IDS = {
  heatmap:       "bin-heatmap",
  clusters:      "bin-clusters",
  clusterLabels: "bin-cluster-labels",
  unclustered:   "bin-unclustered",
  fillBar:       "bin-fill-bar",
};

export function makeCollectionBinsHeatmapLayer(heatSourceId) {
  return {
    id: COLLECTION_BIN_LAYER_IDS.heatmap,
    type: "heatmap",
    source: heatSourceId,
    maxzoom: 19,
    paint: {
      // Floor at 0.3 so even low-fill bins contribute — prevents near-zero density
      "heatmap-weight": ["interpolate", ["linear"], ["get", "fill_level"], 0, 0.3, 100, 1.0],
      // High intensity so the map is clearly visible at default zoom 14
      "heatmap-intensity": ["interpolate", ["linear"], ["zoom"], 11, 2.0, 17, 3.0],
      // Color starts opaque at density 0.05 (not 0.1) so it shows with sparse points
      "heatmap-color": [
        "interpolate", ["linear"], ["heatmap-density"],
        0,    "rgba(0,0,0,0)",
        0.05, "rgba(54,194,212,0.55)",
        0.2,  "rgba(34,197,94,0.7)",
        0.45, "rgba(245,158,11,0.82)",
        0.7,  "rgba(239,68,68,0.9)",
        1.0,  "rgba(185,28,28,1.0)",
      ],
      // Larger radius — each bin illuminates more area
      "heatmap-radius": ["interpolate", ["linear"], ["zoom"], 11, 35, 15, 55, 17, 70],
      "heatmap-opacity": 0.9,
    },
  };
}

export function makeCollectionBinsClusterLayer(sourceId) {
  return {
    id: COLLECTION_BIN_LAYER_IDS.clusters,
    type: "circle",
    source: sourceId,
    filter: ["has", "point_count"],
    layout: { "visibility": "none" },
    paint: {
      "circle-color": CLUSTER_COLOR,
      "circle-radius": CLUSTER_RADIUS,
      "circle-opacity": 0.92,
      "circle-stroke-width": 2,
      "circle-stroke-color": "rgba(6, 10, 18, 0.82)",
    },
  };
}

export function makeCollectionBinsClusterLabelLayer(sourceId) {
  return {
    id: COLLECTION_BIN_LAYER_IDS.clusterLabels,
    type: "symbol",
    source: sourceId,
    filter: ["has", "point_count"],
    layout: {
      "visibility": "none",
      "text-field": "{point_count_abbreviated}",
      "text-size": 13,
      "text-font": ["Open Sans Bold"],
      "text-allow-overlap": true,
    },
    paint: {
      "text-color": "#ffffff",
      "text-halo-color": "rgba(6, 10, 18, 0.4)",
      "text-halo-width": 0.5,
    },
  };
}

export function makeCollectionBinsUnclusteredLayer(sourceId) {
  return {
    id: COLLECTION_BIN_LAYER_IDS.unclustered,
    type: "circle",
    source: sourceId,
    minzoom: 16,
    filter: ["!", ["has", "point_count"]],
    layout: { "visibility": "none" },
    paint: {
      "circle-color": [
        "match", ["get", "status"],
        "normal",           "#22c55e",
        "needs_collection", "#facc15",
        "full",             "#ef4444",
        "issue",            "#a855f7",
        "offline",          "#94a3b8",
        "#38bdf8",
      ],
      "circle-radius": ["interpolate", ["linear"], ["zoom"], 16, 5, 18, 9],
      "circle-stroke-color": "rgba(6, 10, 18, 0.92)",
      "circle-stroke-width": 1.5,
      "circle-opacity": 0.94,
    },
  };
}

export function makeCollectionBinsFillBarLayer(sourceId) {
  return {
    id: COLLECTION_BIN_LAYER_IDS.fillBar,
    type: "symbol",
    source: sourceId,
    minzoom: 15,
    filter: ["!", ["has", "point_count"]],
    layout: {
      "visibility": "none",
      // Percentage text — ASCII only, guaranteed to render in all MapLibre font stacks
      "text-field": ["concat", ["to-string", ["get", "fill_level"]], "%"],
      "text-size": 11,
      "text-font": ["Open Sans Bold"],
      "text-offset": [0, 2.0],
      "text-allow-overlap": true,
      "text-ignore-placement": true,
    },
    paint: {
      "text-color": [
        "case",
        [">=", ["get", "fill_level"], 70], "#ef4444",
        [">=", ["get", "fill_level"], 40], "#f59e0b",
        "#22c55e",
      ],
      "text-halo-color": "rgba(6, 10, 18, 0.85)",
      "text-halo-width": 1.2,
    },
  };
}
