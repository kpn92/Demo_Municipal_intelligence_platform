import useOperationsStore from "../../../store/useOperationsStore.js";
import { formatDateDisplay } from "../../../shared/lib/formatters.js";

function getPendingRoads(allAreaAssignments) {
  return allAreaAssignments
    .filter((a) => ["partially_completed", "incomplete"].includes(String(a.status || "")))
    .flatMap((a) =>
      (a.roadSegments || [])
        .filter((r) => ["incomplete", "pending", "overdue", "failed"].includes(String(r.status || "")))
        .map((r) => ({
          id: `${a.id}:${r.segment_code}`,
          assignmentDate: a.assignmentDate,
          areaCode: a.areaCode,
          areaName: a.areaName,
          groupName: a.groupName,
          roadName: r.road_name || "Οδικό τμήμα",
          priority: Number(r.priority ?? 2),
          status: r.status || "incomplete",
        }))
    )
    .sort((a, b) =>
      String(b.assignmentDate).localeCompare(String(a.assignmentDate)) ||
      a.areaName.localeCompare(b.areaName, "el")
    );
}

const PRIORITY_LABELS = ["Άμεση", "Υψηλή", "Κανονική", "Χαμηλή"];

function PendingRoadsPanel() {
  const allAreaAssignments = useOperationsStore((s) => s.allAreaAssignments);
  const pendingRoads = getPendingRoads(allAreaAssignments);

  return (
    <div className="panel-block pending-roads-panel">
      <div className="section-title">
        <span>Εκκρεμείς Δρόμοι</span>
        <b>{pendingRoads.length}</b>
      </div>
      <div className="pending-roads-list">
        {!pendingRoads.length ? (
          <p className="pending-roads-empty">Δεν υπάρχουν εκκρεμείς δρόμοι.</p>
        ) : (
          pendingRoads.map((item) => (
            <article key={item.id} className="pending-road-row">
              <div>
                <strong>{item.roadName}</strong>
                <span>
                  {formatDateDisplay(item.assignmentDate)} · {item.areaName || item.areaCode} · {item.groupName || "–"}
                </span>
              </div>
              <span className={`priority-badge priority-${item.priority}`}>
                {PRIORITY_LABELS[item.priority] || "–"}
              </span>
            </article>
          ))
        )}
      </div>
    </div>
  );
}

export default PendingRoadsPanel;
