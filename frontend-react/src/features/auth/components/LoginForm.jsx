import { useState } from "react";

function LoginForm({ onSubmit, error, loading }) {
  const [username, setUsername] = useState("supervisor");
  const [password, setPassword] = useState("demo");

  function handleSubmit(e) {
    e.preventDefault();
    onSubmit(username, password);
  }

  return (
    <form className="login-form" onSubmit={handleSubmit}>
      <label>
        Όνομα χρήστη
        <input
          type="text"
          autoComplete="username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="π.χ. supervisor"
        />
      </label>
      <label>
        Κωδικός
        <input
          type="password"
          autoComplete="current-password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="••••••••"
        />
      </label>
      <p className="login-error" role="alert">{error}</p>
      <button type="submit" disabled={loading}>
        {loading ? "Σύνδεση..." : "Σύνδεση"}
      </button>
    </form>
  );
}

export default LoginForm;
