import { create } from "zustand";

function getTodayIso() {
  const now = new Date();
  return new Date(now.getTime() - now.getTimezoneOffset() * 60000)
    .toISOString()
    .slice(0, 10);
}

const INITIAL_COLLECTION_WIZARD = {
  step: 1,
  selectedAreaCodes: [],
  selectedVehicleId: null,
  route: null,
};

const useOperationsStore = create((set, get) => ({
  planDate: getTodayIso(),
  currentView: "people",
  fleetSubTab: "overview",
  assignments: [],
  employees: [],
  areaAssignments: [],
  allAreaAssignments: [],
  gisLayerCache: {},
  visibleContextLayers: new Set(["municipality_boundary", "buildings_25d", "line_roads"]),
  fleetStatusFilter: "all",
  fleetBins: [],
  allFleetBins: [],
  pendingRoads: [],
  mapFitRequest: null,
  mapBounds: null,
  collectionWizard: { ...INITIAL_COLLECTION_WIZARD },

  setPlanDate: (date) => set({ planDate: date }),
  setCurrentView: (view) => {
    const updates = { currentView: view };
    if (view === "fleet") {
      // Always enter fleet in heatmap mode — remove fleet_bins pill if it was left ON
      const next = new Set(get().visibleContextLayers);
      next.delete("fleet_bins");
      updates.visibleContextLayers = next;
    }
    set(updates);
  },
  setFleetSubTab: (tab) => set({ fleetSubTab: tab }),
  setCollectionWizard: (updates) =>
    set((s) => ({ collectionWizard: { ...s.collectionWizard, ...updates } })),
  resetCollectionWizard: () => set({ collectionWizard: { ...INITIAL_COLLECTION_WIZARD } }),
  setAssignments: (assignments) => set({ assignments }),
  setEmployees: (employees) => set({ employees }),
  setAreaAssignments: (areaAssignments) => set({ areaAssignments }),
  setAllAreaAssignments: (allAreaAssignments) => set({ allAreaAssignments }),
  setGisLayer: (layerId, geojson) =>
    set((s) => ({ gisLayerCache: { ...s.gisLayerCache, [layerId]: geojson } })),
  toggleContextLayer: (layerId) => {
    const next = new Set(get().visibleContextLayers);
    if (next.has(layerId)) next.delete(layerId);
    else next.add(layerId);
    set({ visibleContextLayers: next });
  },
  setMapFitRequest: (bbox) => set({ mapFitRequest: bbox }),
  setMapBounds: (bounds) => set({ mapBounds: bounds }),
  setFleetStatusFilter: (filter) => set({ fleetStatusFilter: filter }),
  setFleetBins: (fleetBins) => set({ fleetBins }),
  setAllFleetBins: (allFleetBins) => set({ allFleetBins }),
  selectedFleetArea: null,
  setSelectedFleetArea: (area) => set({ selectedFleetArea: area }),
  setPendingRoads: (pendingRoads) => set({ pendingRoads }),
}));

export default useOperationsStore;
