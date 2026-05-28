import { useState } from "react";
import useAssignmentStore from "../../../store/useAssignmentStore.js";

const LEGEND_ITEMS = [
  { id: "line_roads",           label: "Οδικό δίκτυο",                color: "#5b7089", type: "line" },
  { id: "selected_zone_roads",  label: "Δρόμοι επιλεγμένης περιοχής", color: "#c6f1fb", type: "line" },
  { id: "manual_selected_roads",label: "Επιλεγμένοι δρόμοι",          color: "#ffd166", type: "line" },
  { id: "assigned_roads",       label: "Προγραμματισμένος δρόμος",    color: "#ffd166", type: "line", dashed: false },
  { id: "active_roads",         label: "Δρόμος σε εξέλιξη",           color: "#f59e0b", type: "line" },
  { id: "pending_roads",        label: "Εκκρεμής δρόμος",             color: "#ef4444", type: "line" },
  { id: "completed_roads",      label: "Ολοκληρωμένος δρόμος",        color: "#b9f3d3", type: "line" },
  { id: "assigned_areas",       label: "Ανατεθείσα περιοχή",          color: "#ffd166", type: "area" },
  { id: "active_areas",         label: "Ενεργή περιοχή",              color: "#f59e0b", type: "area" },
  { id: "completed_areas",      label: "Ολοκληρωμένη περιοχή",        color: "#22c55e", type: "area" },
  { id: "incomplete_areas",     label: "Μη ολοκληρωμένη περιοχή",     color: "#e18a6c", type: "area" },
];

function LegendSwatch({ item }) {
  if (item.type === "area") {
    return (
      <span
        className="legend-swatch legend-swatch-area"
        style={{ background: item.color + "44", border: `2px solid ${item.color}` }}
      />
    );
  }
  return (
    <span
      className="legend-swatch legend-swatch-line"
      style={{ background: item.color }}
    />
  );
}

function MapLegend() {
  const [open, setOpen] = useState(false);
  const planningStarted = useAssignmentStore((s) => s.planningStarted);

  const items = planningStarted
    ? LEGEND_ITEMS.filter((i) => ["line_roads", "selected_zone_roads", "manual_selected_roads", "pending_roads"].includes(i.id))
    : LEGEND_ITEMS.filter((i) => ["assigned_roads", "active_roads", "pending_roads", "completed_roads", "assigned_areas", "active_areas", "completed_areas", "incomplete_areas"].includes(i.id));

  return (
    <div className={`map-legend${open ? " map-legend-open" : ""}`}>
      <button
        type="button"
        className="map-legend-toggle"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
      >
        <b>Υπόμνημα</b>
        <small>{open ? "▲" : "▼"}</small>
      </button>
      {open && (
        <div className="map-legend-content">
          {items.map((item) => (
            <div key={item.id} className="map-legend-item">
              <LegendSwatch item={item} />
              <span>{item.label}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default MapLegend;
