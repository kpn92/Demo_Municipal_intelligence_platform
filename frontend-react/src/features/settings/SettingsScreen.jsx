import useNavigationStore from "../../store/useNavigationStore.js";
import useAuthStore from "../../store/useAuthStore.js";
import { useAuth } from "../auth/hooks/useAuth.js";

const SETTING_MODULES = [
  { code: "cleaning", name: "Διαχείριση Καθαριότητας", enabled: true },
  { code: "settings", name: "Ρυθμίσεις", enabled: true },
  { code: "fleet", name: "Στόλος", enabled: false },
  { code: "issues", name: "Βλάβες", enabled: false },
];

const SETTING_USERS = [
  { username: "admin", fullName: "Admin Δήμου", role: "Διαχειριστής", status: "Ενεργός" },
  { username: "supervisor", fullName: "Γ. Παπαδόπουλος", role: "Επόπτης Καθαριότητας", status: "Ενεργός" },
  { username: "fleet", fullName: "Στόλος Καθαριότητας", role: "Χειριστής Στόλου", status: "Demo ανενεργό module" },
];

const SETTING_ROLES = [
  { code: "admin", name: "Διαχειριστής", description: "Πλήρης πρόσβαση σε ενεργά modules και ρυθμίσεις." },
  { code: "cleaning_supervisor", name: "Επόπτης Καθαριότητας", description: "Πρόσβαση στη διαχείριση καθαριότητας και στις αναθέσεις." },
  { code: "fleet_operator", name: "Χειριστής Στόλου", description: "Πρόσβαση στο μελλοντικό module στόλου." },
];

const BUSINESS_RULES = [
  { code: "modules.cleaning.enabled", label: "Module καθαριότητας", value: true },
  { code: "settings.user_management.enabled", label: "Δημιουργία χρηστών", value: true },
  { code: "cleaning.auto_plan.enabled", label: "Αυτόματο πλάνο καθαριότητας", value: true },
  { code: "modules.fleet.enabled", label: "Module στόλου", value: false },
  { code: "modules.issues.enabled", label: "Module βλαβών", value: false },
];

function SettingsScreen() {
  const user = useAuthStore((s) => s.user);
  const setScreen = useNavigationStore((s) => s.setScreen);
  const { logout } = useAuth();

  return (
    <div id="settings-screen">
      <header className="topbar">
        <div className="brand">
          <img className="topbar-logo" src="/assets/keratsini-drapetsona-logo.svg" alt="Δήμος Κερατσινίου - Δραπετσώνας" />
          <div>
            <strong>ΡΥΘΜΙΣΕΙΣ</strong>
            <span>Διαχείριση Συστήματος</span>
          </div>
        </div>
        <div className="operator">
          <button type="button" onClick={() => setScreen("modules")}>Ενότητες</button>
          <span>{user?.name || "Χρήστης"}</span>
          <button type="button" onClick={logout}>Έξοδος</button>
        </div>
      </header>

      <main className="settings-content">
        <section className="settings-section">
          <h2>Modules</h2>
          <div className="settings-table">
            {SETTING_MODULES.map((m) => (
              <div key={m.code} className="settings-row">
                <strong>{m.name}</strong>
                <span className={`settings-status ${m.enabled ? "enabled" : "disabled"}`}>
                  {m.enabled ? "Ενεργό" : "Ανενεργό"}
                </span>
              </div>
            ))}
          </div>
        </section>

        <section className="settings-section">
          <h2>Χρήστες</h2>
          <div className="settings-table">
            {SETTING_USERS.map((u) => (
              <div key={u.username} className="settings-row">
                <strong>{u.fullName}</strong>
                <span>{u.role}</span>
                <span className="settings-status">{u.status}</span>
              </div>
            ))}
          </div>
        </section>

        <section className="settings-section">
          <h2>Ρόλοι</h2>
          <div className="settings-table">
            {SETTING_ROLES.map((r) => (
              <div key={r.code} className="settings-row">
                <strong>{r.name}</strong>
                <span>{r.description}</span>
              </div>
            ))}
          </div>
        </section>

        <section className="settings-section">
          <h2>Κανόνες Λειτουργίας</h2>
          <div className="settings-table">
            {BUSINESS_RULES.map((rule) => (
              <div key={rule.code} className="settings-row">
                <strong>{rule.label}</strong>
                <span className={`settings-status ${rule.value ? "enabled" : "disabled"}`}>
                  {rule.value ? "Ενεργός" : "Ανενεργός"}
                </span>
              </div>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}

export default SettingsScreen;
