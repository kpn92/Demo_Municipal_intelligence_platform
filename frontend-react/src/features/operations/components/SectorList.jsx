import useOperationsStore from "../../../store/useOperationsStore.js";

const STATUS_LABELS = {
  assigned: "Ανατεθειμένη",
  planned: "Προγραμματισμένη",
  in_progress: "Σε εξέλιξη",
  active: "Ενεργή",
  completed: "Ολοκληρωμένη",
  partially_completed: "Μερικώς ολοκλ.",
  incomplete: "Ατελής",
  cancelled: "Ακυρωμένη",
};

function getStatusLabel(status) {
  return STATUS_LABELS[status] || status;
}

function isClosed(status) {
  return ["completed", "cancelled"].includes(status);
}

function SectorList({ onSelectArea }) {
  const planDate = useOperationsStore((s) => s.planDate);
  const areaAssignments = useOperationsStore((s) => s.areaAssignments);

  const forDate = areaAssignments.filter(
    (a) => !planDate || a.assignmentDate === planDate
  );

  const sorted = [...forDate].sort((a, b) =>
    String(a.areaName || "").localeCompare(String(b.areaName || ""), "el")
  );

  if (!sorted.length) {
    return (
      <div className="assignment-sector-row is-empty">
        <div>
          <strong>Χωρίς ανάθεση</strong>
        </div>
      </div>
    );
  }

  return (
    <>
      {sorted.map((assignment) => (
        <div
          key={assignment.id}
          className={`assignment-sector-row is-assigned${isClosed(assignment.status) ? " is-closed" : ""}`}
          role="button"
          tabIndex={0}
          onClick={() => onSelectArea?.(assignment.areaCode)}
          onKeyDown={(e) => e.key === "Enter" && onSelectArea?.(assignment.areaCode)}
          data-assignment-id={assignment.id}
        >
          <div>
            <strong>{assignment.areaName || assignment.areaCode}</strong>
            <span>{assignment.groupName} · {getStatusLabel(assignment.status)}</span>
          </div>
          <b>{assignment.areaCode}</b>
        </div>
      ))}
    </>
  );
}

export default SectorList;
