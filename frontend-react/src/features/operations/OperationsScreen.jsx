import { useState } from "react";
import OperationsTopBar from "./components/OperationsTopBar.jsx";
import KpiStrip from "./components/KpiStrip.jsx";
import FilterPanel from "./components/FilterPanel.jsx";
import SectorList from "./components/SectorList.jsx";
import DetailPanel from "./components/DetailPanel.jsx";
import PendingRoadsPanel from "./components/PendingRoadsPanel.jsx";
import FleetBinsPanel from "./components/FleetBinsPanel.jsx";
import CollectionWizard from "./components/CollectionWizard.jsx";
import CollectionSummaryPanel from "./components/CollectionSummaryPanel.jsx";
import CollectionTimeline from "./components/CollectionTimeline.jsx";
import AssignmentWizard from "../assignments/components/AssignmentWizard.jsx";
import MapContainer from "../map/MapContainer.jsx";
import { useOperationsData } from "./hooks/useOperationsData.js";
import useAssignmentStore from "../../store/useAssignmentStore.js";
import useOperationsStore from "../../store/useOperationsStore.js";

function OperationsScreen() {
  const [selectedAreaCode, setSelectedAreaCode] = useState(null);
  const { reload } = useOperationsData();
  const planningStarted = useAssignmentStore((s) => s.planningStarted);
  const currentView = useOperationsStore((s) => s.currentView);
  const fleetSubTab = useOperationsStore((s) => s.fleetSubTab);
  const setFleetSubTab = useOperationsStore((s) => s.setFleetSubTab);
  const collectionRoute = useOperationsStore((s) => s.collectionWizard.route);
  const collectionStep = useOperationsStore((s) => s.collectionWizard.step);

  const isFleet = currentView === "fleet";
  const isFleetAssignment = isFleet && fleetSubTab === "assignment";
  const showTimeline = isFleetAssignment && collectionStep === 4 && collectionRoute !== null;

  return (
    <div
      id="operations-screen"
      className="twin-shell"
      data-view={currentView}
      data-fleet-subtab={isFleet ? fleetSubTab : undefined}
    >
      <OperationsTopBar />
      <KpiStrip />

      <section className="control-grid">
        {/* Fleet sub-tab bar — spans all columns */}
        {isFleet && (
          <nav className="fleet-subtab-bar" aria-label="Υπο-καρτέλες στόλου">
            <button
              type="button"
              className={fleetSubTab === "overview" ? "active" : ""}
              onClick={() => setFleetSubTab("overview")}
            >
              Επισκόπηση
            </button>
            <button
              type="button"
              className={fleetSubTab === "assignment" ? "active" : ""}
              onClick={() => setFleetSubTab("assignment")}
            >
              Ανάθεση Αποκομιδής
            </button>
          </nav>
        )}

        {/* Left rail */}
        <aside className="left-rail" aria-label="Φίλτρα">
          {isFleet ? (
            fleetSubTab === "overview" ? (
              <FleetBinsPanel />
            ) : (
              <CollectionWizard />
            )
          ) : (
            <>
              <FilterPanel onReload={reload} />

              <div className="panel-block filter-group assigned-areas-panel">
                <div className="section-title">
                  <span>Περιοχές με Ανάθεση</span>
                </div>
                <p className="section-helper">
                  Περιοχές που έχουν ανατεθεί για την επιλεγμένη ημερομηνία.
                </p>
                <div className="filter-list">
                  <SectorList onSelectArea={setSelectedAreaCode} />
                </div>
              </div>

              <div className="panel-block filter-subgroup">
                <div className="section-title">
                  <span>Νέα ανάθεση περιοχής</span>
                </div>
              </div>

              {planningStarted && (
                <AssignmentWizard
                  onComplete={() => { setSelectedAreaCode(null); reload(); }}
                />
              )}

              <div className="twin-note">
                <strong>Digital Twin</strong>
                <p>Ο δήμος αποτυπώνεται σε έναν ενιαίο επιχειρησιακό χάρτη, συνδέοντας περιοχές, δρόμους, σημεία καθαρισμού και διαθέσιμο προσωπικό.</p>
              </div>
            </>
          )}
        </aside>

        {/* Map */}
        <section className="map-stage" aria-label="Επιχειρησιακός χάρτης">
          <MapContainer />
        </section>

        {/* Right rail */}
        <aside className="right-rail" aria-label="Λεπτομέρειες">
          {isFleetAssignment ? (
            <CollectionSummaryPanel />
          ) : (
            <>
              <div className="panel-block">
                <DetailPanel selectedAreaCode={selectedAreaCode} />
              </div>
              <PendingRoadsPanel />
            </>
          )}
        </aside>

        {/* Fleet timeline bar — bottom strip, step 4 only */}
        {showTimeline && <CollectionTimeline />}
      </section>
    </div>
  );
}

export default OperationsScreen;
