import useOperationsStore from "../../../store/useOperationsStore.js";
import { formatMinutes } from "../../../shared/lib/formatters.js";

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

function DetailPanel({ selectedAreaCode }) {
  const areaAssignments = useOperationsStore((s) => s.areaAssignments);

  if (!selectedAreaCode) {
    return (
      <div className="detail-content detail-empty">
        <p>Επιλέξτε μια περιοχή από τη λίστα για να δείτε λεπτομέρειες.</p>
      </div>
    );
  }

  const assignment = areaAssignments.find((a) => a.areaCode === selectedAreaCode);

  if (!assignment) {
    return (
      <div className="detail-content">
        <span className="detail-status">Επιλεγμένη περιοχή</span>
        <h2>{selectedAreaCode}</h2>
        <p>Δεν βρέθηκε ανάθεση για αυτή την περιοχή.</p>
      </div>
    );
  }

  const statusLabel = STATUS_LABELS[assignment.status] || assignment.status;
  const employeesLabel = assignment.employeeNames.length
    ? assignment.employeeNames.join(", ")
    : "Χωρίς επιλογή";

  return (
    <div className="detail-content">
      <span className="detail-status">Ανάθεση περιοχής</span>
      <h2>{assignment.areaName || assignment.areaCode}</h2>
      <p>{assignment.groupName}</p>
      <div className="detail-grid">
        <div><span>Περιοχή</span><b>{assignment.areaCode}</b></div>
        <div><span>Κατάσταση</span><b>{statusLabel}</b></div>
        <div><span>Τμήματα δρόμων</span><b>{assignment.roadSegments?.length || 0}</b></div>
        <div><span>Εκτιμώμενο μήκος</span><b>{assignment.estimatedLengthKm ? `${assignment.estimatedLengthKm.toFixed(2)} χλμ` : "–"}</b></div>
        <div><span>Εκτίμηση χρόνου</span><b>{formatMinutes(assignment.estimatedDurationMin)}</b></div>
        <div><span>Άτομα</span><b>{assignment.requiredPersonnel || "–"}</b></div>
        <div><span>Προσωπικό</span><b>{employeesLabel}</b></div>
      </div>
      {assignment.notes && <p>{assignment.notes}</p>}
    </div>
  );
}

export default DetailPanel;
