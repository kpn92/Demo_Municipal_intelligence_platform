export function formatDateDisplay(iso) {
  if (!iso) return "";
  const [year, month, day] = iso.split("-");
  if (!year || !month || !day) return "";
  return `${day}/${month}/${year}`;
}

export function parseDateDisplay(value) {
  const match = String(value || "").trim().match(/^(\d{2})\/(\d{2})\/(\d{4})$/);
  if (!match) return null;
  const [, day, month, year] = match;
  const iso = `${year}-${month}-${day}`;
  const parsed = new Date(`${iso}T00:00:00`);
  if (Number.isNaN(parsed.getTime())) return null;
  return iso;
}

export function getTodayIso() {
  const now = new Date();
  return new Date(now.getTime() - now.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
}

export function formatMinutes(minutes) {
  if (minutes < 60) return `${minutes}λ`;
  const hours = Math.floor(minutes / 60);
  const rest = minutes % 60;
  return rest ? `${hours}ω ${rest}λ` : `${hours}ω`;
}

export function normalizeSearchText(value) {
  return String(value || "")
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .toLowerCase()
    .trim();
}

export function getPriorityLabel(priority) {
  const labels = { 0: "Άμεση", 1: "Υψηλή", 2: "Κανονική", 3: "Χαμηλή" };
  return labels[Number(priority)] ?? labels[2];
}

export function getPriorityClassName(priority) {
  const classes = { 0: "priority-immediate", 1: "priority-high", 2: "priority-normal", 3: "priority-low" };
  return classes[Number(priority)] ?? classes[2];
}
