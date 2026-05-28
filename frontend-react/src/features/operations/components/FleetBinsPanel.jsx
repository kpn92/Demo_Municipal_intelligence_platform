import { useState } from "react";
import { useFleetData } from "../hooks/useFleetData.js";
import useOperationsStore from "../../../store/useOperationsStore.js";

const STATUS_FILTERS = [
  { id: "all", label: "Όλα" },
  { id: "full", label: "🔴" },
  { id: "needs_collection", label: "🟡" },
  { id: "normal", label: "🟢" },
  { id: "offline", label: "⚫" },
];

const STATUS_LABELS = {
  normal: "Κανονικός",
  needs_collection: "Προς αποκ.",
  full: "Γεμάτος",
  issue: "Πρόβλημα",
  offline: "Εκτός",
};

const STATUS_COLORS = {
  normal: "var(--live)",
  needs_collection: "var(--yellow)",
  full: "var(--red)",
  issue: "var(--violet)",
  offline: "var(--muted)",
};

function getFillColor(pct) {
  if (pct >= 80) return "var(--red)";
  if (pct >= 55) return "var(--yellow)";
  return "var(--live)";
}

function FillBar({ pct }) {
  return (
    <div className="fleet-fill-bar-track">
      <div
        className="fleet-fill-bar-fill"
        style={{ width: `${Math.min(pct, 100)}%`, background: getFillColor(pct) }}
      />
    </div>
  );
}

/* ── Λίστα περιοχών ── */
function AreaList({ areas, statusFilter, onSelectArea }) {
  const totalBins = areas.reduce((s, a) => s + a.total, 0);
  const totalUrgent = areas.reduce(
    (s, a) => s + a.statusCounts.full + a.statusCounts.needs_collection,
    0
  );

  const visible = statusFilter === "all"
    ? areas
    : areas.filter((a) => (a.statusCounts[statusFilter] ?? 0) > 0);

  return (
    <>
      <div className="section-title">
        <span>Περιοχές — Κάδοι</span>
        <b>{totalBins}</b>
      </div>

      {totalUrgent > 0 && (
        <p className="section-helper fleet-urgent-hint">
          ⚠ {totalUrgent} κάδοι χρειάζονται αποκομιδή
        </p>
      )}

      <div className="fleet-area-list">
        {visible.map((area) => {
          const { area_code, area_name, total, avgFill, statusCounts } = area;
          const count = statusFilter === "all" ? total : statusCounts[statusFilter] ?? 0;
          return (
            <button
              key={area_code}
              type="button"
              className="fleet-area-card"
              onClick={() => onSelectArea(area)}
            >
              <div className="fleet-area-header">
                <strong>{area_name}</strong>
                <b>{count} κάδ.</b>
              </div>
              <div className="fleet-area-fill-row">
                <FillBar pct={avgFill} />
                <span>{avgFill}%</span>
              </div>
              <div className="fleet-area-badges">
                {statusCounts.full > 0 && (
                  <span className="fleet-badge badge-full">🔴 {statusCounts.full}</span>
                )}
                {statusCounts.needs_collection > 0 && (
                  <span className="fleet-badge badge-yellow">🟡 {statusCounts.needs_collection}</span>
                )}
                {statusCounts.normal > 0 && (
                  <span className="fleet-badge badge-normal">🟢 {statusCounts.normal}</span>
                )}
                {statusCounts.offline > 0 && (
                  <span className="fleet-badge badge-offline">⚫ {statusCounts.offline}</span>
                )}
              </div>
            </button>
          );
        })}
      </div>
    </>
  );
}

/* ── Λίστα κάδων περιοχής ── */
function BinList({ area, statusFilter, onBack }) {
  const filtered = statusFilter === "all"
    ? area.bins
    : area.bins.filter((b) => b.status === statusFilter);

  const sorted = [...filtered].sort((a, b) => b.fill_level - a.fill_level);

  return (
    <>
      <div className="section-title">
        <button type="button" className="fleet-back-btn" onClick={onBack}>← Πίσω</button>
      </div>

      <div className="fleet-area-detail-header">
        <strong>{area.area_name}</strong>
        <span>{filtered.length} κάδοι</span>
      </div>

      <div className="fleet-area-list">
        {sorted.length === 0 && (
          <p className="section-helper">Δεν υπάρχουν κάδοι για αυτό το φίλτρο.</p>
        )}
        {sorted.map((bin) => (
          <div key={bin.id} className="fleet-bin-row">
            <span
              className="fleet-bin-dot"
              style={{ background: STATUS_COLORS[bin.status] ?? "var(--muted)" }}
            />
            <div className="fleet-bin-info">
              <strong>{bin.road_segment_code ?? bin.bin_code}</strong>
              <FillBar pct={bin.fill_level ?? 0} />
            </div>
            <div className="fleet-bin-right">
              <b style={{ color: getFillColor(bin.fill_level ?? 0) }}>
                {bin.fill_level ?? "—"}%
              </b>
              <small>{STATUS_LABELS[bin.status] ?? bin.status}</small>
            </div>
          </div>
        ))}
      </div>
    </>
  );
}

/* ── Main panel ── */
function FleetBinsPanel() {
  const { areas, loading, error } = useFleetData();
  const [statusFilter, setStatusFilter] = useState("all");
  const selectedArea = useOperationsStore((s) => s.selectedFleetArea);
  const setSelectedFleetArea = useOperationsStore((s) => s.setSelectedFleetArea);

  const handleSelectArea = (area) => setSelectedFleetArea(area);
  const handleBack = () => setSelectedFleetArea(null);

  const handleDropdown = (e) => {
    const val = e.target.value;
    if (val === "all") {
      setSelectedFleetArea(null);
    } else {
      const found = areas.find((a) => String(a.area_code) === val);
      if (found) setSelectedFleetArea(found);
    }
  };

  if (loading) {
    return (
      <div className="panel-block filter-group">
        <div className="section-title"><span>Κάδοι ανά Περιοχή</span></div>
        <p className="section-helper">Φόρτωση κάδων…</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="panel-block filter-group">
        <div className="section-title"><span>Κάδοι ανά Περιοχή</span></div>
        <p className="section-helper" style={{ color: "var(--red)" }}>Σφάλμα φόρτωσης</p>
      </div>
    );
  }

  return (
    <div className="panel-block filter-group fleet-bins-panel">
      {/* Area selector */}
      <select
        className="fleet-area-select"
        value={selectedArea ? String(selectedArea.area_code) : "all"}
        onChange={handleDropdown}
      >
        <option value="all">Όλες οι περιοχές</option>
        {areas.map((a) => (
          <option key={a.area_code} value={String(a.area_code)}>
            {a.area_name}
          </option>
        ))}
      </select>

      {/* Status filter */}
      <div className="fleet-status-filter">
        {STATUS_FILTERS.map((f) => (
          <button
            key={f.id}
            type="button"
            className={statusFilter === f.id ? "active" : ""}
            onClick={() => setStatusFilter(f.id)}
          >
            {f.label}
          </button>
        ))}
      </div>

      {selectedArea ? (
        <BinList area={selectedArea} statusFilter={statusFilter} onBack={handleBack} />
      ) : (
        <AreaList areas={areas} statusFilter={statusFilter} onSelectArea={handleSelectArea} />
      )}
    </div>
  );
}

export default FleetBinsPanel;
