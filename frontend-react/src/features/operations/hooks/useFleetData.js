import { useEffect, useState } from "react";
import client from "../../../api/client.js";
import { ENDPOINTS } from "../../../api/endpoints.js";
import useOperationsStore from "../../../store/useOperationsStore.js";

function computeAreaStats(bins) {
  const statusCounts = { normal: 0, needs_collection: 0, full: 0, issue: 0, offline: 0 };
  let fillSum = 0;

  for (const bin of bins) {
    const s = bin.status;
    if (s in statusCounts) statusCounts[s]++;
    fillSum += bin.fill_level ?? 0;
  }

  const total = bins.length;
  const urgent = statusCounts.full + statusCounts.needs_collection;

  return {
    total,
    avgFill: total > 0 ? Math.round(fillSum / total) : 0,
    statusCounts,
    urgency: total > 0 ? urgent / total : 0,
  };
}

export function useFleetData() {
  const existingBins = useOperationsStore.getState().allFleetBins;
  const [areas, setAreas] = useState(() => {
    if (!existingBins.length) return [];
    const byArea = {};
    for (const bin of existingBins) {
      const key = bin.area_code ?? "—";
      if (!byArea[key]) byArea[key] = { area_code: key, area_name: bin.area_name ?? key, bins: [] };
      byArea[key].bins.push(bin);
    }
    return Object.values(byArea).map((a) => ({ ...a, ...computeAreaStats(a.bins) }));
  });
  const [allBins, setAllBins] = useState(existingBins);
  const [loading, setLoading] = useState(!existingBins.length);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (useOperationsStore.getState().allFleetBins.length > 0) return;
    setLoading(true);
    client
      .get(ENDPOINTS.fleetBins)
      .then(({ data }) => {
        setAllBins(data);
        useOperationsStore.getState().setAllFleetBins(data);

        const byArea = {};
        for (const bin of data) {
          const key = bin.area_code ?? "—";
          if (!byArea[key]) {
            byArea[key] = {
              area_code: bin.area_code ?? "—",
              area_name: bin.area_name ?? bin.area_code ?? "—",
              bins: [],
            };
          }
          byArea[key].bins.push(bin);
        }

        const grouped = Object.values(byArea).map((area) => ({
          ...area,
          ...computeAreaStats(area.bins),
        }));

        // Sort: most urgent first, then alphabetical
        grouped.sort(
          (a, b) =>
            b.urgency - a.urgency ||
            String(a.area_name).localeCompare(String(b.area_name), "el")
        );

        setAreas(grouped);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  return { areas, allBins, loading, error };
}
