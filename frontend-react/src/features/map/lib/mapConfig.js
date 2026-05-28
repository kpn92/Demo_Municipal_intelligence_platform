export const KERATSINI_MAP_VIEW = {
  center: [23.618, 37.9633],
  zoom: 14,
  pitch: 58,
  bearing: -28,
};

export const MAP_STYLE_URL = "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json";

export const MAP_LAYER_PILLS = [
  { id: "municipality_boundary", label: "Όρια Δήμου" },
  { id: "urban_units", label: "Περιοχές" },
  { id: "line_roads", label: "Δρόμοι" },
  { id: "buildings_25d", label: "Κτίρια 2,5D" },
  { id: "land_use_zones", label: "Χρήσεις Γης" },
  { id: "fleet_bins", label: "Κάδοι", fleetOnly: true },
];
