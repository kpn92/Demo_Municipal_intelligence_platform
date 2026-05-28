import { useState } from "react";
import authService from "../services/authService.js";
import useAuthStore from "../../../store/useAuthStore.js";
import useNavigationStore from "../../../store/useNavigationStore.js";

export function useAuth() {
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const setAuth = useAuthStore((s) => s.setAuth);
  const clearAuth = useAuthStore((s) => s.clearAuth);
  const setScreen = useNavigationStore((s) => s.setScreen);

  async function login(username, password) {
    setError("");
    setLoading(true);
    try {
      const user = await authService.login(username, password);
      setAuth(user, null);
      setScreen("modules");
    } catch {
      setError("Λάθος όνομα χρήστη ή κωδικός.");
    } finally {
      setLoading(false);
    }
  }

  function logout() {
    clearAuth();
    setScreen("login");
  }

  return { login, logout, error, loading };
}
