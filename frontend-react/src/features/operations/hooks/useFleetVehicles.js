import { useEffect, useState } from "react";
import client from "../../../api/client.js";
import { ENDPOINTS } from "../../../api/endpoints.js";

const DEMO_VEHICLES = [
  { id: "veh-01", vehicle_code: "Απορριμματοφόρο 1", type: "Απορριμματοφόρο", plate_number: "KHP-4132", status: "available", current_location: { lng: 23.6206, lat: 37.9588 } },
  { id: "veh-02", vehicle_code: "Απορριμματοφόρο 2", type: "Απορριμματοφόρο", plate_number: "KHP-5521", status: "route",     current_location: { lng: 23.6129, lat: 37.9676 } },
  { id: "veh-03", vehicle_code: "Σάρωθρο",           type: "Σάρωθρο",          plate_number: "KHP-6018", status: "route",     current_location: { lng: 23.6264, lat: 37.9607 } },
  { id: "veh-04", vehicle_code: "Pick-up εποπτείας", type: "Εποπτικό",         plate_number: "KHP-7744", status: "maintenance", current_location: { lng: 23.6181, lat: 37.9529 } },
  { id: "veh-05", vehicle_code: "Υδροφόρα",          type: "Υδροφόρα",         plate_number: "KHP-8890", status: "offline",   current_location: { lng: 23.6172, lat: 37.9537 } },
];

export function useFleetVehicles() {
  const [vehicles, setVehicles] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    client
      .get(ENDPOINTS.fleetVehicles)
      .then(({ data }) => setVehicles(data.length ? data : DEMO_VEHICLES))
      .catch(() => setVehicles(DEMO_VEHICLES))
      .finally(() => setLoading(false));
  }, []);

  return { vehicles, loading };
}
