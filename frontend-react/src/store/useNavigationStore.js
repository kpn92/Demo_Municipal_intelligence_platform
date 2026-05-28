import { create } from "zustand";

const useNavigationStore = create((set) => ({
  currentScreen: "login",
  setScreen: (screen) => set({ currentScreen: screen }),
}));

export default useNavigationStore;
