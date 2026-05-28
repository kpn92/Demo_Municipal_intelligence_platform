import apiClient from "../../../api/client.js";
import { ENDPOINTS } from "../../../api/endpoints.js";

export const assignmentsService = {
  async create(payload) {
    const r = await apiClient.post(ENDPOINTS.createCleaningAssignment, payload);
    return r.data;
  },

  buildPayload({ planDate, selectedAreaCode, areaName, selectedGroup, selectedEmployeeIds, employees, roadSegments, priority }) {
    const employeeIds = [...selectedEmployeeIds].map(String);
    const employeeNames = employeeIds
      .map((id) => {
        const emp = employees.find((e) => String(e.id) === id);
        return emp ? `${emp.first_name} ${emp.last_name}` : "";
      })
      .filter(Boolean);

    const estimatedDurationMin = roadSegments.reduce((s, r) => s + Number(r.estimated_duration_min || 0), 0);
    const estimatedLengthKm = roadSegments.reduce((s, r) => s + Number(r.road_length_km || 0), 0);

    const noteParts = [`priority=${priority}`, `mode=roads`];

    return {
      assignment_date: planDate,
      area_code: selectedAreaCode,
      area_name: areaName,
      crew_code: selectedGroup.toLowerCase().replace(/\s+/g, "-"),
      crew_label: selectedGroup,
      employee_ids: employeeIds.map(Number),
      required_personnel: employeeIds.length,
      estimated_duration_min: estimatedDurationMin,
      estimated_length_km: estimatedLengthKm || null,
      notes: noteParts.join("; "),
      road_segments: roadSegments,
    };
  },

  buildRoadSegments(roadFeatures, priority) {
    return roadFeatures.map((feature, index) => {
      const props = feature.properties || {};
      const lengthKm = props.shape_leng ? Number(props.shape_leng) / 1000 : 0;
      return {
        segment_code: String(props.segment_code || props.road_id || props.id || index + 1),
        road_name: props.name || props.ref || props.road_name || `Τμήμα ${index + 1}`,
        status: "assigned",
        planned_order: index + 1,
        priority: Number(priority ?? 2),
        estimated_duration_min: Math.max(8, Math.round(lengthKm * 18)),
        road_length_km: lengthKm || null,
      };
    });
  },
};
