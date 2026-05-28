export const ENDPOINTS = {
  // Auth
  login: "/auth/login",

  // Daily assignments (planning view)
  dailyPlan: (date) => `/daily-assignments/plan?assignment_date=${date}`,
  employees: "/employees",

  // Cleaning plan assignments
  cleaningAssignments: (date) =>
    date ? `/cleaning-plan-assignments?assignment_date=${date}` : "/cleaning-plan-assignments",
  cleaningAssignmentStatus: (id) => `/cleaning-plan-assignments/${id}/status`,
  cleaningAssignment: (id) => `/cleaning-plan-assignments/${id}`,
  createCleaningAssignment: "/cleaning-plan-assignments",

  // Mapping
  cleaningOverview: (date) => `/mapping/cleaning/overview?assignment_date=${date}`,

  // Fleet
  fleetBins: "/fleet/bins",
  fleetVehicles: "/fleet/vehicles",
};

export const CONTEXT_BASE = "/mapping/data/context";
export const CONTEXT_LAYER_URL = (layerId) => `${CONTEXT_BASE}/${layerId}.geojson`;
