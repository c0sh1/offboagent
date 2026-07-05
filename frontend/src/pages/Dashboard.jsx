import { useEffect, useState } from "react";
import { api } from "../api/client";

export default function Dashboard({ onNavigate }) {
  const [stats, setStats] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.getDashboardStats().then(setStats).catch((err) => setError(err.message));
  }, []);

  if (error) return <p className="error">Error: {error}</p>;
  if (!stats) return <p>Cargando resumen...</p>;

  return (
    <div>
      <h2>Resumen</h2>

      <div className="stat-grid">
        <StatCard label="Personas totales" value={stats.total_persons} />
        <StatCard label="Activas" value={stats.active_persons} tone="ok" />
        <StatCard
          label="Offboarding en curso"
          value={stats.offboarding_in_progress}
          tone="warn"
        />
        <StatCard label="Offboardeadas" value={stats.offboarded_persons} />
        <StatCard label="Sistemas conectados" value={stats.systems_count} />
      </div>

      <h3>Señales de riesgo</h3>
      <div className="stat-grid">
        <StatCard
          label="Accesos críticos activos"
          value={stats.critical_active_grants}
          tone={stats.critical_active_grants > 0 ? "danger" : "ok"}
          pulse={stats.critical_active_grants > 0}
          onClick={() => onNavigate("persons")}
        />
        <StatCard
          label="Accesos huérfanos"
          value={stats.orphaned_access_count}
          tone={stats.orphaned_access_count > 0 ? "danger" : "ok"}
          pulse={stats.orphaned_access_count > 0}
          onClick={() => onNavigate("orphaned")}
        />
      </div>
    </div>
  );
}

function StatCard({ label, value, tone = "neutral", pulse = false, onClick }) {
  return (
    <div
      className={`stat-card tone-${tone} ${onClick ? "clickable" : ""}`}
      onClick={onClick}
    >
      <div className="stat-value-row">
        {pulse && <span className="pulse-dot" aria-hidden="true" />}
        <span className="stat-value">{value}</span>
      </div>
      <span className="stat-label">{label}</span>
    </div>
  );
}