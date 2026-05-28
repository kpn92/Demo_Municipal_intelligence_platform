import { useAuth } from "./hooks/useAuth.js";
import LoginForm from "./components/LoginForm.jsx";
import LoginInfoPanel from "./components/LoginInfoPanel.jsx";

function LoginScreen() {
  const { login, error, loading } = useAuth();

  return (
    <main className="login-screen">
      <section className="login-panel">
        <img
          className="municipal-logo-image"
          src="/assets/keratsini-drapetsona-logo.svg"
          alt="Δήμος Κερατσινίου - Δραπετσώνας"
        />
        <div className="login-copy">
          <p className="welcome-line">Καλωσορίσατε στο Σύστημα Επιχειρησιακής Διαχείρισης</p>
          <h1>Είσοδος χρήστη</h1>
          <p>Συνδεθείτε στις ηλεκτρονικές υπηρεσίες του Συστήματος.</p>
        </div>
        <LoginForm onSubmit={login} error={error} loading={loading} />
        <p className="demo-hint">Demo πρόσβαση: <b>supervisor</b> / <b>demo</b></p>
      </section>
      <LoginInfoPanel />
    </main>
  );
}

export default LoginScreen;
