import useNavigationStore from "../../../store/useNavigationStore.js";
import useAuthStore from "../../../store/useAuthStore.js";
import useOperationsStore from "../../../store/useOperationsStore.js";
import { useClock } from "../../../shared/hooks/useClock.js";

const VIEWS = [
  { id: "people", label: "Στελέχωση / Ανάθεση Τομέα" },
  { id: "fleet", label: "Στόλος" },
  { id: "history", label: "Ιστορικό" },
];

function OperationsTopBar() {
  const setScreen = useNavigationStore((s) => s.setScreen);
  const user = useAuthStore((s) => s.user);
  const currentView = useOperationsStore((s) => s.currentView);
  const setCurrentView = useOperationsStore((s) => s.setCurrentView);
  const clock = useClock();

  return (
    <header className="topbar">
      <div className="brand">
        <img className="topbar-logo" src="/assets/keratsini-drapetsona-logo.svg" alt="Δήμος Κερατσινίου - Δραπετσώνας" />
        <div>
          <strong>ΚΑΘΑΡΙΟΤΗΤΑ</strong>
          <span>Επιχειρησιακή Διαχείριση</span>
        </div>
        <b className="live-chip">Ζωντανά</b>
      </div>
      <nav className="nav-tabs" aria-label="Υπομονάδες καθαριότητας">
        {VIEWS.map((v) => (
          <button
            key={v.id}
            type="button"
            className={currentView === v.id ? "active" : ""}
            onClick={() => setCurrentView(v.id)}
          >
            {v.label}
          </button>
        ))}
      </nav>
      <div className="operator">
        <button type="button" onClick={() => setScreen("modules")}>Ενότητες</button>
        <time>{clock}</time>
        <span className="status-dot" />
        <span>{user?.name || "Επόπτης"}</span>
      </div>
    </header>
  );
}

export default OperationsTopBar;
