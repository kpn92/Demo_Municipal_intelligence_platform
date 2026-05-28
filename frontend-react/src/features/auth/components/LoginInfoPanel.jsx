function LoginInfoPanel() {
  return (
    <section className="login-info-panel" aria-label="Πληροφορίες πλατφόρμας">
      <div className="info-inner">
        <p className="info-kicker">Ψηφιακή επιχειρησιακή εικόνα</p>
        <h2>Οι υπηρεσίες του δήμου οργανώνονται ψηφιακά.</h2>

        <div className="info-card">
          <span className="info-icon people-icon" aria-hidden="true">
            <svg viewBox="0 0 48 48">
              <circle cx="24" cy="13" r="6" />
              <circle cx="13" cy="19" r="4.5" />
              <circle cx="35" cy="19" r="4.5" />
              <path d="M15 35v-5c0-5 4-9 9-9s9 4 9 9v5" />
              <path d="M6 35v-4c0-4 3-7 7-7" />
              <path d="M42 35v-4c0-4-3-7-7-7" />
              <path d="M18 35h12" />
            </svg>
          </span>
          <p><b>Ενιαία εικόνα</b> για προσωπικό, περιοχές και καθημερινές αναθέσεις.</p>
        </div>

        <div className="info-card">
          <span className="info-icon shield-icon" aria-hidden="true">
            <svg viewBox="0 0 48 48">
              <path d="M24 5l15 6v11c0 10-6 17-15 21C15 39 9 32 9 22V11l15-6z" />
              <path d="M16 24l6 6 11-13" />
            </svg>
          </span>
          <p><b>Καθαρός δήμος</b> με οπτικοποίηση αρμοδιοτήτων, τομέων και σημείων φροντίδας.</p>
        </div>

        <div className="info-card">
          <span className="info-icon map-icon" aria-hidden="true">
            <svg viewBox="0 0 48 48">
              <path d="M24 43s13-12 13-25a13 13 0 0 0-26 0c0 13 13 25 13 25z" />
              <circle cx="24" cy="18" r="5" />
              <path d="M7 40h12" />
              <path d="M29 40h12" />
              <path d="M7 40l7-8" />
              <path d="M41 40l-7-8" />
            </svg>
          </span>
          <p><b>Χάρτης εργασιών</b>, ιστορικό και επιχειρησιακά στοιχεία σε πραγματικό χρόνο.</p>
        </div>
      </div>
    </section>
  );
}

export default LoginInfoPanel;
