import useOperationsStore from "../../../store/useOperationsStore.js";
import { formatMinutes } from "../../../shared/lib/formatters.js";

function CollectionSummaryPanel() {
  const cw = useOperationsStore((s) => s.collectionWizard);
  const hasArea = cw.selectedAreaCodes.length > 0;
  const hasVehicle = cw.selectedVehicleId !== null;
  const hasRoute = cw.route !== null;

  const badge = hasRoute ? "Έτοιμο" : hasVehicle ? "Βήμα 3" : hasArea ? "Βήμα 2" : "Αναμονή";
  const { route } = cw;

  return (
    <section className="fleet-assignment-summary-card panel-block">
      <div className="section-title">
        <span>Σύνοψη ανάθεσης</span>
        <b>{badge}</b>
      </div>

      {!hasArea ? (
        <p className="wizard-hint">Ολοκληρώστε τα βήματα για σύνοψη ανάθεσης.</p>
      ) : (
        <div className="fleet-assign-summary-grid">
          <div className="fleet-assign-summary-item" style={{ gridColumn: "1/-1" }}>
            <span>Περιοχές</span>
            <b>{cw.selectedAreaCodes.join(", ")}</b>
          </div>
          <div className="fleet-assign-summary-item">
            <span>Όχημα</span>
            <b>{route ? route.vehicle.vehicle_code ?? route.vehicle.id : "—"}</b>
          </div>
          <div className="fleet-assign-summary-item">
            <span>Πινακίδα</span>
            <b>{route ? route.vehicle.plate_number : "—"}</b>
          </div>
          {route && (
            <>
              <div className="fleet-assign-summary-item">
                <span>Κάδοι</span>
                <b>{route.totalBins}</b>
              </div>
              <div className="fleet-assign-summary-item">
                <span>Δρομολόγια</span>
                <b>{route.totalTrips}</b>
              </div>
              <div className="fleet-assign-summary-item">
                <span>Εκτιμ. χρόνος</span>
                <b>{formatMinutes(route.estimatedMinutes)}</b>
              </div>
              <div className="fleet-assign-summary-item">
                <span>Εκτιμ. km</span>
                <b>{route.estimatedKm} km</b>
              </div>
              <div className="fleet-assign-summary-item">
                <span>🔴 Γεμάτοι</span>
                <b>{route.redCount}</b>
              </div>
              <div className="fleet-assign-summary-item">
                <span>🟡 Μισοί</span>
                <b>{route.yellowCount}</b>
              </div>
            </>
          )}
        </div>
      )}

      <div className="fleet-priority-legend">
        <p className="fleet-priority-legend-title">Σειρά προτεραιότητας αποκομιδής</p>
        <div className="fleet-priority-row">
          <span className="prio-red">●</span>
          <span>Γεμάτοι κάδοι (&gt;70%) — πρώτα</span>
        </div>
        <div className="fleet-priority-row">
          <span className="prio-yellow">●</span>
          <span>Μισοί κάδοι (41–70%) — δεύτεροι</span>
        </div>
        <div className="fleet-priority-row">
          <span className="prio-green">●</span>
          <span>Ελαφροί κάδοι (&lt;40%) — τρίτοι</span>
        </div>
        <p className="wizard-hint" style={{ marginTop: "6px" }}>
          Εντός κάθε κατηγορίας: βέλτιστη γεωγραφική σειρά.
        </p>
      </div>
    </section>
  );
}

export default CollectionSummaryPanel;
