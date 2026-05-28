import { ROAD_LAYER_STYLES, AREA_STATUS_STYLES, FLAT_FOOTPRINT_IDS, EXTRUDED_FOOTPRINT_IDS, FLAT_FOOTPRINT_AREA_LIMIT, FLEET_BINS_SOURCE_OPTIONS } from "./layerDefinitions.js";
import { getContextFillColor, getContextLineColor, getContextFillOpacity, getContextLineWidth, getContextLineOpacity, getRoadLineWidth, getRoadHitWidth, getRoadCasingWidth, getRoadCasingColor, getRoadCasingOpacity } from "./styleHelpers.js";

const ROAD_LAYER_IDS = new Set(["line_roads","selected_zone_roads","manual_selected_roads","hover_road","assigned_roads","active_roads","pending_roads","priority_roads","completed_roads"]);
const AREA_LAYER_IDS = new Set(["unassigned_areas","assigned_areas","active_areas","completed_areas","incomplete_areas"]);
const BASEMAP_BUILDINGS_LAYER_ID = "basemap-buildings-25d";

function getFirstSymbolLayerId(map) {
  return map.getStyle()?.layers?.find((l) => l.type === "symbol")?.id;
}

function getVectorBasemapSourceId(map) {
  const sources = map.getStyle()?.sources || {};
  if (sources.carto?.type === "vector") return "carto";
  return Object.entries(sources).find(([, s]) => s.type === "vector")?.[0];
}

export function bringContextLayersToFront(map) {
  const ordered = [
    "context-buildings_25d-extrusion","context-land_use_zones-fill","context-land_use_zones-outline","context-land_use_zones-label",
    "context-cleaning_areas-fill","context-cleaning_areas-outline","context-cleaning_areas2-fill","context-cleaning_areas2-outline",
    "context-urban_units-fill","context-urban_units-outline","context-urban_units-label",
    "context-unassigned_areas-fill","context-unassigned_areas-outline","context-assigned_areas-fill","context-assigned_areas-outline",
    "context-active_areas-fill","context-active_areas-outline","context-completed_areas-fill","context-completed_areas-outline",
    "context-incomplete_areas-fill","context-incomplete_areas-outline",
    "context-line_roads-hit","context-line_roads-casing","context-line_roads-line","context-line_roads-label",
    "context-selected_zone_roads-hit","context-selected_zone_roads-casing","context-selected_zone_roads-line","context-selected_zone_roads-label",
    "context-manual_selected_roads-hit","context-manual_selected_roads-casing","context-manual_selected_roads-line","context-manual_selected_roads-label",
    "context-hover_road-hit","context-hover_road-casing","context-hover_road-line",
    "context-assigned_roads-casing","context-assigned_roads-line","context-active_roads-casing","context-active_roads-line",
    "context-pending_roads-casing","context-pending_roads-line","context-priority_roads-casing","context-priority_roads-line",
    "context-completed_roads-casing","context-completed_roads-line",
    "context-selected_area_highlight-fill","context-selected_area_highlight-outline",
    "context-road_selection_polygon-fill","context-road_selection_polygon-outline",
    "context-municipality_boundary-outline",
    "context-fleet_bins-clusters",
    "context-fleet_bins-cluster-count",
    "context-fleet_bins-point",
    "context-fleet_bins-label",
  ];
  if (map.getLayer(BASEMAP_BUILDINGS_LAYER_ID)) map.moveLayer(BASEMAP_BUILDINGS_LAYER_ID, getFirstSymbolLayerId(map));
  ordered.forEach((id) => { if (map.getLayer(id)) map.moveLayer(id); });
}

export function setContextLayerVisibility(map, layerId, visibility) {
  const sourceId = `context-${layerId}`;
  [`${sourceId}-extrusion`,`${sourceId}-hit`,`${sourceId}-casing`,`${sourceId}-line`,`${sourceId}-point`,`${sourceId}-fill`,`${sourceId}-outline`,`${sourceId}-outline-casing`,`${sourceId}-label`,`${sourceId}-clusters`,`${sourceId}-cluster-count`].forEach((id) => {
    if (map.getLayer(id)) map.setLayoutProperty(id, "visibility", visibility);
  });
}

export function applyContextLayer(map, layerId, geojson) {
  const sourceId = `context-${layerId}`;
  const existing = map.getSource(sourceId);

  if (existing) {
    existing.setData(geojson);
    setContextLayerVisibility(map, layerId, "visible");
    bringContextLayersToFront(map);
    return;
  }

  if (layerId === "fleet_bins") {
    map.addSource(sourceId, { type: "geojson", data: geojson, ...FLEET_BINS_SOURCE_OPTIONS });

    const clusterColor = [
      "case",
      [">", ["get", "count_red"],    0], "#ef4444",
      [">", ["get", "count_orange"], 0], "#f97316",
      "#22c55e",
    ];

    map.addLayer({
      id: `${sourceId}-clusters`,
      type: "circle",
      source: sourceId,
      filter: ["has", "point_count"],
      paint: {
        "circle-color": clusterColor,
        "circle-radius": ["step", ["get", "point_count"], 14, 10, 18, 30, 22],
        "circle-opacity": 0.88,
        "circle-stroke-width": 2,
        "circle-stroke-color": "rgba(6, 10, 18, 0.85)",
      },
    });

    map.addLayer({
      id: `${sourceId}-cluster-count`,
      type: "symbol",
      source: sourceId,
      filter: ["has", "point_count"],
      layout: {
        "text-field": "{point_count_abbreviated}",
        "text-font": ["Open Sans Semibold"],
        "text-size": 11,
        "text-allow-overlap": true,
      },
      paint: {
        "text-color": "#ffffff",
        "text-halo-color": "rgba(6, 10, 18, 0.35)",
        "text-halo-width": 0.5,
      },
    });

    map.addLayer({
      id: `${sourceId}-point`,
      type: "circle",
      source: sourceId,
      filter: ["!", ["has", "point_count"]],
      paint: {
        "circle-color": ["match", ["get", "status"],
          "normal",           "#22c55e",
          "needs_collection", "#f97316",
          "full",             "#ef4444",
          "issue",            "#a855f7",
          "offline",          "#94a3b8",
          "#38bdf8",
        ],
        "circle-radius": ["interpolate", ["linear"], ["zoom"], 16, 4.5, 18, 7.2],
        "circle-stroke-color": "rgba(6, 10, 18, 0.92)",
        "circle-stroke-width": ["interpolate", ["linear"], ["zoom"], 16, 1, 18, 1.5],
        "circle-opacity": 0.92,
      },
    });

    map.addLayer({
      id: `${sourceId}-label`,
      type: "symbol",
      source: sourceId,
      filter: ["!", ["has", "point_count"]],
      layout: {
        "text-field": ["concat", ["to-string", ["get", "fill_level"]], "%"],
        "text-size": ["interpolate", ["linear"], ["zoom"], 16, 0, 17, 11],
        "text-font": ["Open Sans Bold"],
        "text-anchor": "top",
        "text-offset": [0, 1.1],
        "text-allow-overlap": true,
        "text-optional": true,
      },
      paint: {
        "text-color": [
          "case",
          ["any", ["==", ["get", "status"], "issue"], ["==", ["get", "status"], "offline"]], "#9ca3af",
          [">=", ["to-number", ["get", "fill_level"]], 70], "#ef4444",
          [">=", ["to-number", ["get", "fill_level"]], 40], "#f97316",
          "#22c55e",
        ],
        "text-halo-color": "rgba(6, 10, 18, 0.9)",
        "text-halo-width": 1.5,
      },
    });

    bringContextLayersToFront(map);
    return;
  }

  map.addSource(sourceId, { type: "geojson", data: geojson });

  if (layerId === "buildings_25d") {
    map.addLayer({
      id: `${sourceId}-extrusion`, type: "fill-extrusion", source: sourceId, minzoom: 11,
      filter: ["all",["!",["in",["to-number",["get","id"]],["literal",FLAT_FOOTPRINT_IDS]]],["any",["in",["to-number",["get","id"]],["literal",EXTRUDED_FOOTPRINT_IDS]],["<",["to-number",["get","shape_area"]],FLAT_FOOTPRINT_AREA_LIMIT]]],
      paint: {
        "fill-extrusion-color": ["interpolate",["linear"],["zoom"],11,"#245a74",16,"#60a5fa"],
        "fill-extrusion-height": ["case",[">",["to-number",["get","shape_area"]],500],30,[">",["to-number",["get","shape_area"]],250],22,[">",["to-number",["get","shape_area"]],120],16,12],
        "fill-extrusion-base": 0, "fill-extrusion-opacity": 0.82, "fill-extrusion-vertical-gradient": true,
      },
    });
    bringContextLayersToFront(map);
    return;
  }

  if (ROAD_LAYER_IDS.has(layerId)) {
    map.addLayer({ id: `${sourceId}-hit`, type: "line", source: sourceId, layout: { "line-cap": "round", "line-join": "round" }, paint: { "line-color": "#ffffff", "line-width": getRoadHitWidth(layerId), "line-opacity": 0.01 } });
    map.addLayer({ id: `${sourceId}-casing`, type: "line", source: sourceId, layout: { "line-cap": "round", "line-join": "round" }, paint: { "line-color": getRoadCasingColor(layerId), "line-width": getRoadCasingWidth(layerId), "line-opacity": getRoadCasingOpacity(layerId) } });
    map.addLayer({ id: `${sourceId}-line`, type: "line", source: sourceId, layout: { "line-cap": "round", "line-join": "round" }, paint: { "line-color": getContextLineColor(layerId), "line-width": getRoadLineWidth(layerId), "line-opacity": getContextLineOpacity(layerId), ...(layerId === "priority_roads" ? { "line-dasharray": [1.1, 1.1] } : {}) } });
    if (["line_roads","selected_zone_roads","manual_selected_roads"].includes(layerId)) {
      map.addLayer({ id: `${sourceId}-label`, type: "symbol", source: sourceId, minzoom: layerId === "line_roads" ? 12.8 : 11.8, layout: { "symbol-placement": "line-center", "text-field": ["coalesce",["get","name"],["get","ref"],["get","road_name"]], "text-size": ["interpolate",["linear"],["zoom"],12,10.5,15,13.5,17,15], "text-font": ["Open Sans Semibold"], "text-letter-spacing": 0, "text-rotation-alignment": "map", "text-pitch-alignment": "viewport", "text-allow-overlap": layerId !== "line_roads", "text-ignore-placement": layerId !== "line_roads" }, paint: { "text-color": layerId === "line_roads" ? "#dbeafe" : "#ffffff", "text-opacity": ["interpolate",["linear"],["zoom"],12,0.82,15,1], "text-halo-color": "rgba(6, 10, 18, 0.94)", "text-halo-width": layerId === "line_roads" ? 1.35 : 1.8, "text-halo-blur": 0.35 } });
    }
    bringContextLayersToFront(map);
    return;
  }

  if (AREA_LAYER_IDS.has(layerId)) {
    const style = AREA_STATUS_STYLES[layerId];
    map.addLayer({ id: `${sourceId}-fill`, type: "fill", source: sourceId, paint: { "fill-color": style.fill, "fill-opacity": style.fillOpacity } });
    map.addLayer({ id: `${sourceId}-outline`, type: "line", source: sourceId, paint: { "line-color": style.outline, "line-width": style.outlineWidth, "line-opacity": style.outlineOpacity } });
    bringContextLayersToFront(map);
    return;
  }

  if (layerId === "selected_area_highlight") {
    map.addLayer({ id: `${sourceId}-fill`, type: "fill", source: sourceId, paint: { "fill-color": "#f0b84b", "fill-opacity": 0.14 } });
    map.addLayer({ id: `${sourceId}-outline-casing`, type: "line", source: sourceId, paint: { "line-color": "rgba(27, 19, 8, 0.9)", "line-width": 5.5, "line-opacity": 0.82 } });
    map.addLayer({ id: `${sourceId}-outline`, type: "line", source: sourceId, paint: { "line-color": "#ffd166", "line-width": 3.6, "line-opacity": 1, "line-dasharray": [2.4, 1.6] } });
    bringContextLayersToFront(map);
    return;
  }

  map.addLayer({ id: `${sourceId}-fill`, type: "fill", source: sourceId, paint: { "fill-color": getContextFillColor(layerId, geojson), "fill-opacity": getContextFillOpacity(layerId) } });
  map.addLayer({ id: `${sourceId}-outline`, type: "line", source: sourceId, paint: { "line-color": getContextLineColor(layerId), "line-width": getContextLineWidth(layerId), "line-opacity": getContextLineOpacity(layerId) } });

  if (layerId === "urban_units") {
    map.addLayer({ id: `${sourceId}-label`, type: "symbol", source: sourceId, layout: { "text-field": ["coalesce",["get","perigrafi"],["get","onoma"]], "text-size": ["interpolate",["linear"],["zoom"],11,11,15,14], "text-font": ["Open Sans Semibold"], "text-letter-spacing": 0, "text-anchor": "center", "text-allow-overlap": false, "text-ignore-placement": false }, paint: { "text-color": "#e6f1f8", "text-opacity": 0.92, "text-halo-color": "rgba(9, 16, 26, 0.92)", "text-halo-width": 1.1, "text-halo-blur": 0.4 } });
  }

  if (layerId === "land_use_zones") {
    map.addLayer({ id: `${sourceId}-label`, type: "symbol", source: sourceId, minzoom: 12.8, layout: { "text-field": ["get","onomasia"], "text-size": ["interpolate",["linear"],["zoom"],12.8,9,15,12,17,14], "text-font": ["Open Sans Semibold"], "text-letter-spacing": 0, "text-anchor": "center", "text-allow-overlap": false, "text-ignore-placement": false }, paint: { "text-color": "#ffffff", "text-opacity": ["interpolate",["linear"],["zoom"],12.8,0.78,15,0.96], "text-halo-color": "rgba(15, 23, 42, 0.9)", "text-halo-width": 1.2, "text-halo-blur": 0.35 } });
  }

  bringContextLayersToFront(map);
}

export function removeContextLayer(map, layerId) {
  setContextLayerVisibility(map, layerId, "none");
}

export function applyBasemapBuildingsLayer(map) {
  if (map.getLayer(BASEMAP_BUILDINGS_LAYER_ID)) {
    map.setLayoutProperty(BASEMAP_BUILDINGS_LAYER_ID, "visibility", "visible");
    bringContextLayersToFront(map);
    return;
  }
  const sourceId = getVectorBasemapSourceId(map);
  if (!sourceId) return;
  map.addLayer({
    id: BASEMAP_BUILDINGS_LAYER_ID, type: "fill-extrusion", source: sourceId, "source-layer": "building", minzoom: 13,
    paint: {
      "fill-extrusion-color": ["interpolate",["linear"],["zoom"],13,"#19324a",16,"#3b82c4"],
      "fill-extrusion-height": ["interpolate",["linear"],["zoom"],13,0,14.4,["case",["has","render_height"],["to-number",["get","render_height"]],["has","height"],["to-number",["get","height"]],["has","levels"],["*",["to-number",["get","levels"]],3],16]],
      "fill-extrusion-base": ["case",["has","render_min_height"],["to-number",["get","render_min_height"]],["has","min_height"],["to-number",["get","min_height"]],0],
      "fill-extrusion-opacity": 0.68, "fill-extrusion-vertical-gradient": true,
    },
  }, getFirstSymbolLayerId(map));
  bringContextLayersToFront(map);
}

export function removeBasemapBuildingsLayer(map) {
  if (map.getLayer(BASEMAP_BUILDINGS_LAYER_ID)) map.setLayoutProperty(BASEMAP_BUILDINGS_LAYER_ID, "visibility", "none");
}
