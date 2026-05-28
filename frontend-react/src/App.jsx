import useNavigationStore from "./store/useNavigationStore.js";
import useAuthStore from "./store/useAuthStore.js";
import LoginScreen from "./features/auth/LoginScreen.jsx";
import ModuleScreen from "./features/modules/ModuleScreen.jsx";
import OperationsScreen from "./features/operations/OperationsScreen.jsx";
import SettingsScreen from "./features/settings/SettingsScreen.jsx";
import { useEffect } from "react";

function App() {
  const screen = useNavigationStore((s) => s.currentScreen);
  const user = useAuthStore((s) => s.user);
  const setScreen = useNavigationStore((s) => s.setScreen);

  useEffect(() => {
    if (!user && screen !== "login") setScreen("login");
  }, [user, screen, setScreen]);

  return (
    <>
      {screen === "login" && <LoginScreen />}
      {screen === "modules" && <ModuleScreen />}
      {screen === "operations" && <OperationsScreen />}
      {screen === "settings" && <SettingsScreen />}
    </>
  );
}

export default App;
