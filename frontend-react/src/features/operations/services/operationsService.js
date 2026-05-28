import apiClient from "../../../api/client.js";
import { ENDPOINTS } from "../../../api/endpoints.js";

function normalizeAssignment(raw) {
  // Backend returns crew_label (not group_name) and employees[] (not employee_ids)
  const employeesNested = raw.employees || [];
  return {
    id: raw.id,
    areaCode: String(raw.area_code || raw.areaCode || ""),
    areaName: raw.area_name || raw.areaName || "",
    groupName: raw.crew_label || raw.group_name || raw.groupName || "",
    assignmentDate: String(raw.assignment_date || raw.assignmentDate || ""),
    status: raw.status || "assigned",
    notes: raw.notes || "",
    employeeIds: employeesNested.length
      ? employeesNested.map((e) => String(e.employee_id ?? e.employee?.id ?? "")).filter(Boolean)
      : (raw.employee_ids || raw.employeeIds || []).map(String),
    employeeNames: employeesNested.length
      ? employeesNested.map((e) => `${e.employee?.first_name || ""} ${e.employee?.last_name || ""}`.trim()).filter(Boolean)
      : (raw.employee_names || raw.employeeNames || []),
    requiredPersonnel: raw.required_personnel || raw.requiredPersonnel || 0,
    estimatedLengthKm: Number(raw.estimated_length_km || raw.estimatedLengthKm || 0),
    estimatedDurationMin: raw.estimated_duration_min || raw.estimatedDurationMin || 0,
    roadSegments: raw.road_segments || raw.roadSegments || [],
  };
}

export const operationsService = {
  async loadPlanData(date) {
    const [assignments, employees, areaAssignments, allAreaAssignments] = await Promise.all([
      apiClient.get(ENDPOINTS.dailyPlan(date)).then((r) => r.data),
      apiClient.get(ENDPOINTS.employees).then((r) => r.data),
      apiClient.get(ENDPOINTS.cleaningAssignments(date)).then((r) => r.data).catch(() => []),
      apiClient.get(ENDPOINTS.cleaningAssignments()).then((r) => r.data).catch(() => []),
    ]);
    return {
      assignments: assignments || [],
      employees: employees || [],
      areaAssignments: (areaAssignments || []).map(normalizeAssignment),
      allAreaAssignments: ((allAreaAssignments || []).length ? allAreaAssignments : areaAssignments || []).map(normalizeAssignment),
    };
  },

  async updateAssignmentStatus(id, status) {
    const r = await apiClient.patch(ENDPOINTS.cleaningAssignmentStatus(id), { status });
    return r.data;
  },

  async deleteAssignment(id) {
    const r = await apiClient.delete(ENDPOINTS.cleaningAssignment(id));
    return r.data;
  },
};
