import useOperationsStore from "../../../store/useOperationsStore.js";
import { MAP_LAYER_PILLS } from "../lib/mapConfig.js";

function MapLayerPills() {
  const visibleContextLayers = useOperationsStore((s) => s.visibleContextLayers);
  const toggleContextLayer   = useOperationsStore((s) => s.toggleContextLayer);
  const currentView          = useOperationsStore((s) => s.currentView);

  const pills = MAP_LAYER_PILLS.filter((p) => !p.fleetOnly || currentView === "fleet");

  return (
    <div className="map-layer-pills">
      {pills.map((pill) => (
        <button
          key={pill.id}
          type="button"
          className={visibleContextLayers.has(pill.id) ? "active" : ""}
          onClick={() => toggleContextLayer(pill.id)}
        >
          {pill.label}
        </button>
      ))}
    </div>
  );
}

export default MapLayerPills;
