import useOperationsStore from "../../../store/useOperationsStore.js";

const FLEET_VEHICLES = [
  { id: "veh-01", status: "available", fuel: 82 },
  { id: "veh-02", status: "route", fuel: 64 },
  { id: "veh-03", status: "route", fuel: 57 },
  { id: "veh-04", status: "maintenance", fuel: 43 },
  { id: "veh-05", status: "offline", fuel: 28 },
];

export function useKpis() {
  const currentView = useOperationsStore((s) => s.currentView);
  const employees = useOperationsStore((s) => s.employees);
  const areaAssignments = useOperationsStore((s) => s.areaAssignments);
  const assignments = useOperationsStore((s) => s.assignments);

  if (currentView === "fleet") {
    const active = FLEET_VEHICLES.filter((v) => v.status === "route").length;
    const available = FLEET_VEHICLES.filter((v) => v.status === "available").length;
    const unavailable = FLEET_VEHICLES.filter((v) => ["maintenance", "offline"].includes(v.status)).length;
    const avgFuel = Math.round(FLEET_VEHICLES.reduce((s, v) => s + v.fuel, 0) / FLEET_VEHICLES.length);
    return {
      pending: { label: "Διαθέσιμα Οχήματα", value: String(available), sub: "έτοιμα" },
      crews: { label: "Δρομολόγια Στόλου", value: String(active), sub: "σε κίνηση" },
      vehicles: { label: "Κατάσταση Στόλου", value: `${active + available} / ${FLEET_VEHICLES.length}`, sub: "ενεργά / σύνολο" },
      hotzones: { label: "Εκτός Υπηρεσίας", value: String(unavailable), sub: "βλάβη / συντήρηση" },
      coverage: { label: "Μέση Στάθμη Καυσίμου", value: `${avgFuel}%`, sub: "στόλος" },
    };
  }

  const assignedEmployeeIds = new Set(areaAssignments.flatMap((a) => a.employeeIds));
  const available = employees.filter((e) => !assignedEmployeeIds.has(String(e.id))).length;
  const planned = areaAssignments.filter((a) => !["completed", "cancelled"].includes(a.status));

  const sectorIds = new Set(assignments.map((a) => a.sector_id).filter(Boolean));
  const highLoadSectors = [...sectorIds].filter((sid) => {
    const minutes = assignments
      .filter((a) => a.sector_id === sid)
      .flatMap((a) => a.filteredItems || [])
      .reduce((s, item) => s + (item.estimated_minutes || 30), 0);
    return minutes >= 250;
  });

  return {
    pending: { label: "Διαθέσιμο Προσωπικό", value: String(available), sub: "για ανάθεση" },
    crews: { label: "Συνεργεία σε Πλάνο", value: String(planned.length), sub: "ενεργά" },
    vehicles: { label: "Κατάσταση Οχημάτων", value: "3 / 5", sub: "ενεργά / σύνολο" },
    hotzones: { label: "Περιοχές Αυξημένου Φόρτου", value: String(highLoadSectors.length), sub: "βάσει εκτίμησης" },
    coverage: { label: "Ανατεθειμένο Προσωπικό", value: String(assignedEmployeeIds.size), sub: "άτομα" },
  };
}
