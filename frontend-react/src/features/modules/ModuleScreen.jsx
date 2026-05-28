import useAuthStore from "../../store/useAuthStore.js";
import useNavigationStore from "../../store/useNavigationStore.js";
import { useAuth } from "../auth/hooks/useAuth.js";
import ModuleCard from "./components/ModuleCard.jsx";

const MODULES = [
  {
    id: "cleaning",
    title: "Διαχείριση Καθαριότητας",
    description: "Σχεδιασμός συνεργείων, περιοχών και ημερήσιων εργασιών.",
    enabled: true,
  },
  {
    id: "settings",
    title: "Ρυθμίσεις",
    description: "Διαχείριση χρηστών, ρόλων, δικαιωμάτων και βασικών παραμέτρων συστήματος.",
    enabled: true,
  },
];

function ModuleScreen() {
  const user = useAuthStore((s) => s.user);
  const setScreen = useNavigationStore((s) => s.setScreen);
  const { logout } = useAuth();

  function handleOpen(moduleId) {
    if (moduleId === "settings") setScreen("settings");
    else if (moduleId === "cleaning") setScreen("operations");
  }

  return (
    <main className="module-screen">
      <header className="module-header">
        <div className="module-brand">
          <img src="/assets/keratsini-drapetsona-logo.svg" alt="Δήμος Κερατσινίου - Δραπετσώνας" />
          <div>
            <strong>Δήμος Κερατσινίου - Δραπετσώνας</strong>
            <p>Ψηφιακή Επιχειρησιακή Διαχείριση</p>
          </div>
        </div>
        <div className="user-chip">
          <b>{user?.name ?? "Χρήστης"}</b>
          <button type="button" onClick={logout}>Έξοδος</button>
        </div>
      </header>

      <section className="module-intro">
        <p className="session-meta">2 ενεργά λειτουργικά συστήματα · Ρόλος: Επόπτης</p>
        <p className="eyebrow">Ενεργά λειτουργικά συστήματα</p>
        <h1>Πού θέλεις να εργαστείς;</h1>
        <p>Λογαριασμός δοκιμής · Επόπτης καθαριότητας</p>
      </section>

      <section className="module-workspace">
        <section className="module-grid">
          {MODULES.map((m) => (
            <ModuleCard key={m.id} module={m} onOpen={handleOpen} />
          ))}
        </section>
        <aside className="module-summary" aria-label="Σύνοψη λειτουργίας">
          <p className="summary-kicker">Γενική εικόνα λειτουργίας</p>
          <h2>Καθαριότητα:<br />επιχειρησιακά διαθέσιμη</h2>
          <div className="summary-map">
            <span className="summary-pin pin-a" />
            <span className="summary-pin pin-b" />
            <span className="summary-pin pin-c" />
            <span className="summary-pin pin-d" />
          </div>
          <div className="summary-row"><span>Εργασίες πλάνου</span><b>22</b></div>
          <div className="summary-row"><span>Ενεργά συνεργεία</span><b>7</b></div>
          <div className="summary-row"><span>Περιοχές υψηλού φόρτου</span><b>3</b></div>
          <p className="summary-note">Τελευταία ενημέρωση: πριν 5 λεπτά.</p>
        </aside>
      </section>
    </main>
  );
}

export default ModuleScreen;
