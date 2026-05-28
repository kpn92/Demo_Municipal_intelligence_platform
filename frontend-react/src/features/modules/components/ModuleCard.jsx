function CleaningIcon() {
  return (
    <span className="module-icon cleaning" aria-hidden="true">
      <svg viewBox="0 0 48 48">
        <path d="M8 40h32" />
        <path d="M14 40V20l10-12 10 12v20" />
        <path d="M20 40v-8h8v8" />
        <path d="M10 24H6l18-18 18 18h-4" />
      </svg>
    </span>
  );
}

function SettingsIcon() {
  return (
    <span className="module-icon" aria-hidden="true">
      <svg viewBox="0 0 48 48">
        <circle cx="24" cy="24" r="5" />
        <path d="M24 8v4M24 36v4M8 24h4M36 24h4M12.7 12.7l2.8 2.8M32.5 32.5l2.8 2.8M35.3 12.7l-2.8 2.8M15.5 32.5l-2.8 2.8" />
      </svg>
    </span>
  );
}

function ModuleCard({ module, onOpen }) {
  const isSettings = module.id === "settings";

  return (
    <article className={`module-card${!module.enabled ? " locked" : ""}`}>
      {isSettings ? <SettingsIcon /> : <CleaningIcon />}
      <h2>{module.title}</h2>
      {module.enabled && <em className="module-status">Διαθέσιμο</em>}
      <p>{module.description}</p>
      <button
        type="button"
        onClick={() => module.enabled && onOpen(module.id)}
        disabled={!module.enabled}
      >
        {module.enabled ? "Είσοδος" : "Μη διαθέσιμο"}
      </button>
    </article>
  );
}

export default ModuleCard;
