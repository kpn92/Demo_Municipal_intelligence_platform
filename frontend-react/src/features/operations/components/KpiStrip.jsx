import { useKpis } from "../hooks/useKpis.js";

function KpiCard({ kpi, type }) {
  return (
    <article className={`kpi-card${type ? ` ${type}` : ""}`}>
      <span>{kpi.label}</span>
      <strong>{kpi.value}</strong>
      <small>{kpi.sub}</small>
    </article>
  );
}

function KpiStrip() {
  const kpis = useKpis();

  return (
    <section className="kpi-strip" aria-label="Επιχειρησιακή σύνοψη ημέρας">
      <KpiCard kpi={kpis.pending} type="people" />
      <KpiCard kpi={kpis.crews} type="crews" />
      <KpiCard kpi={kpis.vehicles} type="vehicles" />
      <KpiCard kpi={kpis.hotzones} type="hotzones" />
      <KpiCard kpi={kpis.coverage} type="coverage" />
    </section>
  );
}

export default KpiStrip;
