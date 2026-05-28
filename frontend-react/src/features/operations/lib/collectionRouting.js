// Pure routing logic — no React, no state

const VEHICLE_CAPACITY_BINS = {
  "Απορριμματοφόρο": 35,
};

const DEFAULT_START = [23.62, 37.96];

export function getVehicleCapacityBins(type) {
  return VEHICLE_CAPACITY_BINS[type] ?? 0;
}

export function isVehicleSuitable(vehicle) {
  return (
    getVehicleCapacityBins(vehicle.type) > 0 &&
    vehicle.status !== "maintenance" &&
    vehicle.status !== "offline"
  );
}

export function getCollectionAreas(bins) {
  const map = new Map();
  for (const bin of bins) {
    const code = bin.area_code;
    if (!code) continue;
    if (!map.has(code)) {
      map.set(code, { code, name: bin.area_name || `Περιοχή ${code}`, total: 0, red: 0, yellow: 0 });
    }
    const area = map.get(code);
    area.total++;
    if (bin.fill_level >= 70) area.red++;
    else if (bin.fill_level >= 40) area.yellow++;
  }
  return [...map.values()].sort(
    (a, b) => (b.red - a.red) || (b.yellow - a.yellow) || a.name.localeCompare(b.name, "el"),
  );
}

export function getBinSummaryForAreas(areaCodes, bins) {
  const filtered = bins.filter((b) => areaCodes.includes(b.area_code));
  const red = filtered.filter((b) => b.fill_level >= 70).length;
  const yellow = filtered.filter((b) => b.fill_level >= 40 && b.fill_level < 70).length;
  return { total: filtered.length, needsCollection: red + yellow, red, yellow };
}

function nearestNeighborSort(bins, startPos) {
  if (!bins.length) return [];
  const remaining = [...bins];
  let [curLng, curLat] = startPos;
  const sorted = [];
  while (remaining.length) {
    let bestIdx = 0;
    let bestDist = Infinity;
    for (let i = 0; i < remaining.length; i++) {
      const b = remaining[i];
      const dx = (Number(b.location.lng) - curLng) * Math.cos((curLat * Math.PI) / 180);
      const dy = Number(b.location.lat) - curLat;
      const d = dx * dx + dy * dy;
      if (d < bestDist) { bestDist = d; bestIdx = i; }
    }
    const nearest = remaining.splice(bestIdx, 1)[0];
    sorted.push(nearest);
    curLng = Number(nearest.location.lng);
    curLat = Number(nearest.location.lat);
  }
  return sorted;
}

export function computeCollectionRoute(areaCodes, vehicle, bins) {
  const capacity = getVehicleCapacityBins(vehicle.type);
  if (!capacity) return null;

  const validBins = bins.filter(
    (b) =>
      areaCodes.includes(b.area_code) &&
      Number.isFinite(Number(b.location?.lng)) &&
      Number.isFinite(Number(b.location?.lat)),
  );
  if (!validBins.length) return null;

  const start = vehicle.current_location
    ? [vehicle.current_location.lng, vehicle.current_location.lat]
    : DEFAULT_START;

  const redBins = nearestNeighborSort(validBins.filter((b) => b.fill_level >= 70), start);
  const yellowBins = nearestNeighborSort(
    validBins.filter((b) => b.fill_level >= 40 && b.fill_level < 70),
    start,
  );
  const greenBins = nearestNeighborSort(validBins.filter((b) => b.fill_level < 40), start);
  const allSorted = [...redBins, ...yellowBins, ...greenBins];

  const trips = [];
  for (let i = 0; i < allSorted.length; i += capacity) {
    trips.push(allSorted.slice(i, i + capacity));
  }
  const totalBins = allSorted.length;
  const totalTrips = trips.length;

  return {
    vehicle,
    trips,
    allBins: allSorted,
    totalBins,
    totalTrips,
    estimatedMinutes: Math.round(totalBins * 3 + totalTrips * 20),
    estimatedKm: Math.round((totalBins * 0.08 + totalTrips * 5) * 10) / 10,
    redCount: redBins.length,
    yellowCount: yellowBins.length,
    greenCount: greenBins.length,
  };
}

export function getInterpolatedPosition(allBins, progress) {
  const coords = allBins.map((b) => [Number(b.location.lng), Number(b.location.lat)]);
  if (!coords.length) return DEFAULT_START;
  if (coords.length === 1) return coords[0];
  const segments = coords.length - 1;
  const pos = progress * segments;
  const segIdx = Math.min(Math.floor(pos), segments - 1);
  const t = pos - segIdx;
  const [lng1, lat1] = coords[segIdx];
  const [lng2, lat2] = coords[segIdx + 1];
  return [lng1 + (lng2 - lng1) * t, lat1 + (lat2 - lat1) * t];
}
