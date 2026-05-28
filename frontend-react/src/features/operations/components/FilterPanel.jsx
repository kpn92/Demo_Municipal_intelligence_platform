import useOperationsStore from "../../../store/useOperationsStore.js";
import useAssignmentStore from "../../../store/useAssignmentStore.js";
import { formatDateDisplay, parseDateDisplay } from "../../../shared/lib/formatters.js";

function FilterPanel({ onReload }) {
  const planDate = useOperationsStore((s) => s.planDate);
  const setPlanDate = useOperationsStore((s) => s.setPlanDate);
  const planningStarted = useAssignmentStore((s) => s.planningStarted);
  const startPlanning = useAssignmentStore((s) => s.startPlanning);
  const cancelPlanning = useAssignmentStore((s) => s.cancelPlanning);

  function handleDisplayChange(e) {
    const iso = parseDateDisplay(e.target.value);
    if (iso) setPlanDate(iso);
  }

  function handleNativeChange(e) {
    if (e.target.value) setPlanDate(e.target.value);
  }

  return (
    <div className="panel-block filter-group">
      <div className="section-title">
        <span>Φίλτρα</span>
      </div>
      <label className="field">
        Ημερομηνία
        <div className="date-input-row">
          <input
            type="text"
            inputMode="numeric"
            placeholder="dd/mm/yyyy"
            value={formatDateDisplay(planDate)}
            onChange={handleDisplayChange}
          />
          <input
            className="native-date-input"
            type="date"
            value={planDate}
            onChange={handleNativeChange}
          />
        </div>
      </label>
      <button type="button" className="primary-button" onClick={onReload}>
        Εφαρμογή φίλτρων
      </button>

      <div className="plan-action-row">
        {!planningStarted ? (
          <button type="button" className="primary-button" onClick={startPlanning}>
            Εκκίνηση
          </button>
        ) : (
          <button type="button" className="secondary-button" onClick={cancelPlanning}>
            Εκκαθάριση ανάθεσης
          </button>
        )}
      </div>
      {!planningStarted && (
        <p className="plan-assignment-hint">
          Με την εκκίνηση θα φωτιστούν οι περιοχές στον χάρτη για επιλογή.
        </p>
      )}
    </div>
  );
}

export default FilterPanel;
