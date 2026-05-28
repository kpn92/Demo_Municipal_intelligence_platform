import { create } from "zustand";

const useAssignmentStore = create((set) => ({
  planningStarted: false,
  wizardStep: 1,
  selectedAreaCode: null,
  selectedRoadCodes: new Set(),
  selectedGroup: "",
  selectedEmployeeIds: new Set(),
  assignmentPriority: 2,
  roadClickActive: false,
  roadPolygonActive: false,

  startPlanning: () => set({ planningStarted: true, wizardStep: 1, selectedAreaCode: null, selectedRoadCodes: new Set(), selectedGroup: "", selectedEmployeeIds: new Set() }),
  cancelPlanning: () => set({ planningStarted: false, wizardStep: 1, selectedAreaCode: null, selectedRoadCodes: new Set(), selectedGroup: "", selectedEmployeeIds: new Set(), roadClickActive: false, roadPolygonActive: false }),
  setWizardStep: (step) => set({ wizardStep: step }),
  setSelectedAreaCode: (code) => set({ selectedAreaCode: code }),
  toggleRoadCode: (code) =>
    set((s) => {
      const next = new Set(s.selectedRoadCodes);
      if (next.has(code)) next.delete(code);
      else next.add(code);
      return { selectedRoadCodes: next };
    }),
  setSelectedRoadCodes: (codes) => set({ selectedRoadCodes: new Set(codes) }),
  clearRoadCodes: () => set({ selectedRoadCodes: new Set() }),
  setSelectedGroup: (group) => set({ selectedGroup: group }),
  toggleEmployee: (id) =>
    set((s) => {
      const next = new Set(s.selectedEmployeeIds);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return { selectedEmployeeIds: next };
    }),
  setAssignmentPriority: (priority) => set({ assignmentPriority: priority }),
  setRoadClickActive: (active) => set({ roadClickActive: active }),
  setRoadPolygonActive: (active) => set({ roadPolygonActive: active }),
}));

export default useAssignmentStore;
