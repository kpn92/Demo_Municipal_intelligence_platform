import { useState } from "react";
import { useAssignmentWizard } from "../hooks/useAssignmentWizard.js";
import useOperationsStore from "../../../store/useOperationsStore.js";
import useAssignmentStore from "../../../store/useAssignmentStore.js";

const GROUP_OPTIONS = Array.from({ length: 10 }, (_, i) => `Ομάδα ${i + 1}`);
const PRIORITY_OPTIONS = [
  { value: 3, label: "Χαμηλή" },
  { value: 2, label: "Κανονική" },
  { value: 1, label: "Υψηλή" },
  { value: 0, label: "Άμεση" },
];
const STEP_TITLES = ["Επιλογή περιοχής", "Επιλογή δρόμων", "Συνεργείο", "Έλεγχος"];
const COMPLETED_STATUSES = new Set(["completed", "partially_completed", "incomplete"]);

function isCompletedStatus(status) {
  return COMPLETED_STATUSES.has(String(status || ""));
}

function getEmployeeStatus(employeeId, areaAssignments) {
  const active = areaAssignments.find(
    (a) => !isCompletedStatus(a.status) && (a.employeeIds || []).includes(String(employeeId))
  );
  if (!active) return { label: "Ελεύθερος", tone: "free" };
  if (isCompletedStatus(active.status)) return { label: "Ολοκληρώθηκε", tone: "completed" };
  return { label: "Σε πλάνο", tone: "planned" };
}

function AssignmentWizard({ onComplete }) {
  const {
    wizardStep, selectedAreaCode, selectedGroup, selectedEmployeeIds, assignmentPriority,
    roadClickActive,
    cleaningAreas, employees, areaRoads, selectedRoadFeatures,
    canGoNext, next, prev, submit, submitting, error,
    setSelectedAreaCode, setSelectedGroup, setAssignmentPriority, toggleEmployee, cancel,
    selectAllRoads, selectVisibleRoads, addPendingRoads, clearRoads, toggleRoadClick,
  } = useAssignmentWizard(onComplete);
  const areaAssignments = useOperationsStore((s) => s.areaAssignments);
  const selectedRoadCodes = useAssignmentStore((s) => s.selectedRoadCodes);
  const toggleRoadCode = useAssignmentStore((s) => s.toggleRoadCode);

  return (
    <section className="work-card assignment-builder">
      <div className="assignment-wizard-header">
        <div>
          <span>Οδηγός Ανάθεσης</span>
          <h3>Βήμα {wizardStep}: {STEP_TITLES[wizardStep - 1]}</h3>
        </div>
        <b>{wizardStep}/4</b>
      </div>

      <div className="assignment-wizard-steps" aria-label="Βήματα">
        {STEP_TITLES.map((title, i) => (
          <button
            key={i + 1}
            type="button"
            className={wizardStep === i + 1 ? "active" : ""}
            onClick={() => {}}
          >
            {i + 1} {title.split(" ")[0]}
          </button>
        ))}
      </div>

      <div className="assignment-wizard-panel">
        {wizardStep === 1 && (
          <StepAreaSelect
            areas={cleaningAreas}
            selectedAreaCode={selectedAreaCode}
            onSelect={setSelectedAreaCode}
          />
        )}
        {wizardStep === 2 && (
          <StepRoadSelect
            roads={areaRoads}
            selectedRoadCodes={selectedRoadCodes}
            onToggleRoad={toggleRoadCode}
            roadClickActive={roadClickActive}
            onToggleRoadClick={toggleRoadClick}
            onSelectAll={selectAllRoads}
            onSelectVisible={selectVisibleRoads}
            onAddPending={addPendingRoads}
            onClear={clearRoads}
          />
        )}
        {wizardStep === 3 && (
          <StepCrewSelect
            employees={employees}
            selectedEmployeeIds={selectedEmployeeIds}
            onToggleEmployee={toggleEmployee}
            selectedGroup={selectedGroup}
            onGroupChange={setSelectedGroup}
            priority={assignmentPriority}
            onPriorityChange={setAssignmentPriority}
            areaAssignments={areaAssignments}
            selectedAreaCode={selectedAreaCode}
          />
        )}
        {wizardStep === 4 && (
          <StepReview
            selectedAreaCode={selectedAreaCode}
            selectedGroup={selectedGroup}
            selectedEmployeeIds={selectedEmployeeIds}
            employees={employees}
            roadCount={selectedRoadFeatures.length}
            priority={assignmentPriority}
            error={error}
          />
        )}
      </div>

      <div className="assignment-wizard-nav">
        <button type="button" className="secondary-button" onClick={wizardStep === 1 ? cancel : prev}>
          {wizardStep === 1 ? "Ακύρωση" : "Πίσω"}
        </button>
        {wizardStep < 4 ? (
          <button type="button" className="primary-button" onClick={next} disabled={!canGoNext()}>
            Συνέχεια
          </button>
        ) : (
          <button type="button" className="primary-button" onClick={submit} disabled={submitting}>
            {submitting ? "Αποθήκευση…" : "Οριστικοποίηση"}
          </button>
        )}
      </div>
    </section>
  );
}

function StepAreaSelect({ areas, selectedAreaCode, onSelect }) {
  const areaOptions = areas
    .map((f) => {
      const p = f.properties || {};
      const code = String(p.area_code || p.gid || "");
      const name = p.onoma || p.perigrafi || code;
      return { code, name };
    })
    .filter((o) => o.code)
    .sort((a, b) => a.name.localeCompare(b.name, "el"));

  return (
    <label className="field">
      Περιοχή
      <select value={selectedAreaCode || ""} onChange={(e) => onSelect(e.target.value)}>
        <option value="">Επιλέξτε περιοχή…</option>
        {areaOptions.map((o) => (
          <option key={o.code} value={o.code}>{o.name}</option>
        ))}
      </select>
    </label>
  );
}

function StepRoadSelect({
  roads, selectedRoadCodes, onToggleRoad,
  roadClickActive, onToggleRoadClick,
  onSelectAll, onSelectVisible, onAddPending, onClear,
}) {
  const [search, setSearch] = useState("");

  const hasArea = roads.length > 0;
  const selectedCount = selectedRoadCodes.size;
  const allSelected = hasArea && selectedCount === roads.length;

  const filteredRoads = search.trim()
    ? roads.filter((f) => {
        const name = (f.properties?.name || f.properties?.road_name || f.properties?.ref || "").toLowerCase();
        return name.includes(search.trim().toLowerCase());
      })
    : roads;

  return (
    <div className="step-road-select">
      <div className="road-select-summary">
        <span className="road-select-count">
          {hasArea
            ? `${selectedCount} / ${roads.length} τμήματα επιλεγμένα`
            : "Δεν βρέθηκαν δρόμοι για αυτή την περιοχή"}
        </span>
      </div>

      <div className="road-select-toolbar">
        <button
          type="button"
          className={`road-tool-btn${roadClickActive ? " is-active" : ""}`}
          disabled={!hasArea}
          onClick={onToggleRoadClick}
          title="Επιλογή δρόμου με κλικ στον χάρτη"
        >
          Κλικ χάρτη
        </button>
        <button
          type="button"
          className="road-tool-btn"
          disabled={!hasArea}
          onClick={onSelectAll}
          title="Επιλογή όλων των δρόμων της περιοχής"
        >
          Όλοι
        </button>
        <button
          type="button"
          className="road-tool-btn"
          disabled={!hasArea}
          onClick={onSelectVisible}
          title="Επιλογή δρόμων που είναι ορατοί στον χάρτη"
        >
          Ορατοί
        </button>
        <button
          type="button"
          className="road-tool-btn"
          disabled={!hasArea}
          onClick={onAddPending}
          title="Προσθήκη εκκρεμών δρόμων"
        >
          Εκκρεμείς
        </button>
        <button
          type="button"
          className="road-tool-btn road-tool-clear"
          disabled={!selectedCount}
          onClick={onClear}
          title="Καθαρισμός επιλογής"
        >
          Καθαρισμός
        </button>
      </div>

      {hasArea && (
        <>
          <input
            type="search"
            className="road-search-input"
            placeholder="Αναζήτηση δρόμου…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <div className="road-list">
            {filteredRoads.length === 0 && (
              <p className="section-helper">Δεν βρέθηκαν αποτελέσματα.</p>
            )}
            {filteredRoads.map((f) => {
              const p = f.properties || {};
              const code = String(p.segment_code || p.road_id || p.id || "");
              const name = p.name || p.road_name || p.ref || code || "–";
              const checked = selectedRoadCodes.has(code);
              return (
                <label key={code || name} className={`road-list-item${checked ? " is-selected" : ""}`}>
                  <input
                    type="checkbox"
                    checked={checked}
                    onChange={() => code && onToggleRoad(code)}
                  />
                  <span>{name}</span>
                </label>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
}

function StepCrewSelect({
  employees, selectedEmployeeIds, onToggleEmployee,
  selectedGroup, onGroupChange,
  priority, onPriorityChange,
  areaAssignments, selectedAreaCode,
}) {
  const activeEmployees = employees.filter((e) => e.is_active !== false);
  const hasGroup = Boolean(selectedGroup);

  const lockedGroups = new Set(
    (areaAssignments || [])
      .filter((a) => !isCompletedStatus(a.status) && a.areaCode !== selectedAreaCode)
      .map((a) => a.groupName)
      .filter(Boolean)
  );

  return (
    <>
      <label className="field">
        Προτεραιότητα
        <select value={priority} onChange={(e) => onPriorityChange(Number(e.target.value))}>
          {PRIORITY_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </select>
      </label>

      <label className="field">
        Συνεργείο
        <select value={selectedGroup} onChange={(e) => onGroupChange(e.target.value)}>
          <option value="" disabled>Επιλέξτε Ομάδα</option>
          {GROUP_OPTIONS.map((g) => (
            <option key={g} value={g} disabled={lockedGroups.has(g)}>{g}</option>
          ))}
        </select>
      </label>

      <label className="field">
        Προσωπικό Συνεργείου
        <div className="employee-checklist" aria-disabled={!hasGroup}>
          {activeEmployees.length === 0 && (
            <p className="section-helper">Δεν βρέθηκε προσωπικό.</p>
          )}
          {activeEmployees.map((emp) => {
            const empId = String(emp.id);
            const assignment = (areaAssignments || []).find(
              (a) => !isCompletedStatus(a.status) && (a.employeeIds || []).includes(empId)
            );
            const assignedToOther = assignment && assignment.areaCode !== selectedAreaCode;
            const isLocked = !hasGroup || assignedToOther;
            const status = getEmployeeStatus(empId, areaAssignments || []);
            return (
              <label
                key={empId}
                className={`employee-option${isLocked ? " is-disabled" : ""}`}
              >
                <input
                  type="checkbox"
                  checked={selectedEmployeeIds.has(empId)}
                  onChange={() => !isLocked && onToggleEmployee(empId)}
                  disabled={isLocked}
                />
                <span>{emp.first_name} {emp.last_name}</span>
                <b className={`employee-status employee-status-${status.tone}`}>
                  {status.label}
                </b>
              </label>
            );
          })}
        </div>
      </label>
    </>
  );
}

function StepReview({ selectedAreaCode, selectedGroup, selectedEmployeeIds, employees, roadCount, priority, error }) {
  const PRIORITY_LABELS = { 0: "Άμεση", 1: "Υψηλή", 2: "Κανονική", 3: "Χαμηλή" };
  const employeeNames = [...selectedEmployeeIds]
    .map((id) => {
      const emp = employees.find((e) => String(e.id) === id);
      return emp ? `${emp.first_name} ${emp.last_name}` : "";
    })
    .filter(Boolean);

  return (
    <div className="assignment-wizard-review">
      <div className="detail-grid">
        <div><span>Περιοχή</span><b>{selectedAreaCode || "–"}</b></div>
        <div><span>Ομάδα</span><b>{selectedGroup || "–"}</b></div>
        <div><span>Δρόμοι</span><b>{roadCount}</b></div>
        <div><span>Προτεραιότητα</span><b>{PRIORITY_LABELS[priority]}</b></div>
        <div><span>Άτομα</span><b>{selectedEmployeeIds.size}</b></div>
        <div><span>Προσωπικό</span><b>{employeeNames.join(", ") || "–"}</b></div>
      </div>
      {error && <p className="assignment-error">{error}</p>}
      <p>Ελέγξτε τη σύνοψη και οριστικοποιήστε την ανάθεση.</p>
    </div>
  );
}

export default AssignmentWizard;
