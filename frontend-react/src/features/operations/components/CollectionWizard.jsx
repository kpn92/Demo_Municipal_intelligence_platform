import { useCollectionWizard } from "../hooks/useCollectionWizard.js";
import { getVehicleCapacityBins, isVehicleSuitable } from "../lib/collectionRouting.js";
import { formatMinutes } from "../../../shared/lib/formatters.js";

const STEP_TITLES = ["", "Επιλογή περιοχής", "Επιλογή οχήματος", "Πρόταση διαδρομής", "Εκτέλεση"];

const STATUS_LABELS = {
  all: "Όλα",
  available: "Διαθέσιμο",
  route: "Σε δρομολόγιο",
  maintenance: "Συντήρηση",
  offline: "Εκτός",
};

function Step1({ areas, selectedAreaCodes, binSummary, toggleArea }) {
  if (!areas.length) {
    return <p className="wizard-hint">Φόρτωση περιοχών…</p>;
  }
  return (
    <>
      <p className="wizard-hint">Επιλέξτε περιοχές για αποκομιδή.</p>
      <div className="collection-area-grid">
        {areas.map((area) => (
          <button
            key={area.code}
            type="button"
            className={`collection-area-chip${selectedAreaCodes.includes(area.code) ? " active" : ""}`}
            onClick={() => toggleArea(area.code)}
          >
            <span>{area.name}</span>
            <div className="collection-area-stats">
              {area.red > 0 && <b className="stat-red">● {area.red}</b>}
              {area.yellow > 0 && <b className="stat-yellow">● {area.yellow}</b>}
              <small>{area.total}</small>
            </div>
          </button>
        ))}
      </div>
      {binSummary && (
        <div className="collection-bin-summary">
          <b>{binSummary.needsCollection}</b>
          <span>προς αποκομιδή</span>
          <small>{binSummary.red} κόκκ. · {binSummary.yellow} κίτρ.</small>
        </div>
      )}
    </>
  );
}

function Step2({ vehicles, selectedVehicleId, binSummary, selectVehicle }) {
  return (
    <>
      {binSummary && (
        <div className="collection-bin-summary">
          <b>{binSummary.needsCollection}</b>
          <span>κάδοι για αποκομιδή</span>
        </div>
      )}
      <p className="wizard-hint">Επιλέξτε απορριμματοφόρο.</p>
      <div className="collection-vehicle-list">
        {vehicles.map((v) => {
          const cap = getVehicleCapacityBins(v.type);
          const suitable = isVehicleSuitable(v);
          const needed = binSummary?.needsCollection ?? 0;
          const trips = cap > 0 ? Math.ceil(needed / cap) : null;
          const fits = cap > 0 && needed <= cap;
          const isSelected = String(v.id) === String(selectedVehicleId);
          return (
            <button
              key={v.id}
              type="button"
              className={`collection-vehicle-card${isSelected ? " active" : ""}${!suitable ? " is-disabled" : ""}`}
              disabled={!suitable}
              onClick={() => selectVehicle(v.id)}
            >
              <span className={`fleet-status-dot fleet-status-${v.status}`} />
              <div className="collection-vehicle-info">
                <strong>{v.vehicle_code ?? v.id}</strong>
                <small>{v.plate_number} · {STATUS_LABELS[v.status] ?? v.status}</small>
                <small className={!cap ? "muted-text" : ""}>
                  {cap
                    ? `${cap} κάδοι/δρομολ.${trips ? ` → ${trips}×` : ""}`
                    : "Μη κατάλληλο"}
                </small>
              </div>
              {suitable && <b>{fits ? "✓ Αρκεί" : `${trips}×`}</b>}
            </button>
          );
        })}
      </div>
    </>
  );
}

function Step3({ route }) {
  if (!route) return <p className="wizard-hint">Υπολογισμός διαδρομής…</p>;
  return (
    <div className="collection-estimate">
      <div className="collection-estimate-grid">
        <div><b>{route.totalBins}</b><span>κάδοι</span></div>
        <div><b>{formatMinutes(route.estimatedMinutes)}</b><span>εκτίμηση</span></div>
        <div><b>{route.estimatedKm} km</b><span>διαδρομή</span></div>
        <div><b>{route.totalTrips}</b><span>δρομολόγια</span></div>
      </div>
      <div className="collection-priority-summary">
        <span className="prio-red">● {route.redCount} κόκκινοι (&gt;70%)</span>
        <span className="prio-yellow">● {route.yellowCount} κίτρινοι (40–70%)</span>
        <span className="prio-green">● {route.greenCount} πράσινοι (&lt;40%)</span>
      </div>
      {route.totalTrips > 1 && (
        <p className="wizard-hint">Απαιτούνται {route.totalTrips} δρομολόγια λόγω χωρητικότητας.</p>
      )}
      <p className="wizard-hint">Η διαδρομή εμφανίζεται στον χάρτη. Συνεχίστε για εκτέλεση.</p>
    </div>
  );
}

function Step4({ route }) {
  if (!route) return <p className="wizard-hint">Δεν υπάρχει διαδρομή.</p>;
  return (
    <>
      <div className="collection-summary">
        <div className="collection-estimate-grid">
          <div><b>{route.totalBins}</b><span>κάδοι</span></div>
          <div><b>{formatMinutes(route.estimatedMinutes)}</b><span>εκτίμηση</span></div>
          <div><b>{route.estimatedKm} km</b><span>διαδρομή</span></div>
          <div><b>{route.totalTrips}×</b><span>δρομολόγια</span></div>
        </div>
      </div>
      <div className="collection-priority-summary">
        <span className="prio-red">● {route.redCount} κόκκινοι (&gt;70%)</span>
        <span className="prio-yellow">● {route.yellowCount} κίτρινοι (40–70%)</span>
        <span className="prio-green">● {route.greenCount} πράσινοι (&lt;40%)</span>
      </div>
      <p className="wizard-hint">
        Χρησιμοποιήστε την κάτω μπάρα για εκτέλεση animation διαδρομής.
      </p>
    </>
  );
}

function CollectionWizard() {
  const {
    step,
    selectedAreaCodes,
    selectedVehicleId,
    route,
    areas,
    vehicles,
    binSummary,
    loading,
    isStepValid,
    toggleArea,
    selectVehicle,
    nextStep,
    prevStep,
    reset,
  } = useCollectionWizard();

  if (loading && !areas.length) {
    return (
      <section className="work-card fleet-collection-wizard">
        <p className="wizard-hint">Φόρτωση δεδομένων…</p>
      </section>
    );
  }

  const isLastStep = step === 4;
  const canNext = isStepValid(step);

  return (
    <section className="work-card fleet-collection-wizard">
      <div className="assignment-wizard-header">
        <div>
          <span>Ανάθεση αποκομιδής</span>
          <h3>Βήμα {step}: {STEP_TITLES[step]}</h3>
        </div>
        <b>{step}/4</b>
      </div>

      <div className="assignment-wizard-steps">
        {[1, 2, 3, 4].map((s) => (
          <button
            key={s}
            type="button"
            className={`${step === s ? "active" : ""}${s < step ? " is-done" : ""}`}
            disabled={s > step}
          >
            {s} {["Περιοχή", "Όχημα", "Διαδρομή", "Εκτέλεση"][s - 1]}
          </button>
        ))}
      </div>

      <div className="assignment-wizard-panel">
        {step === 1 && (
          <Step1
            areas={areas}
            selectedAreaCodes={selectedAreaCodes}
            binSummary={binSummary}
            toggleArea={toggleArea}
          />
        )}
        {step === 2 && (
          <Step2
            vehicles={vehicles}
            selectedVehicleId={selectedVehicleId}
            binSummary={binSummary}
            selectVehicle={selectVehicle}
          />
        )}
        {step === 3 && <Step3 route={route} />}
        {step === 4 && <Step4 route={route} />}
      </div>

      <div className="assignment-wizard-nav">
        {step > 1 && (
          <button type="button" className="secondary-button" onClick={prevStep}>
            Πίσω
          </button>
        )}
        <button
          type="button"
          className="primary-button"
          disabled={!isLastStep && !canNext}
          onClick={isLastStep ? reset : nextStep}
          style={{ marginLeft: step === 1 ? "auto" : undefined }}
        >
          {isLastStep ? "Επαναφορά" : "Συνέχεια"}
        </button>
      </div>
    </section>
  );
}

export default CollectionWizard;
