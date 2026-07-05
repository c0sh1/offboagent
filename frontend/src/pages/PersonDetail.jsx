import { useEffect, useState } from "react";
import { api } from "../api/client";

const RISK_ORDER = { critical: 0, high: 1, medium: 2, low: 3 };

export default function PersonDetail({ personId, onBack }) {
  const [person, setPerson] = useState(null);
  const [systems, setSystems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [initiatedBy, setInitiatedBy] = useState("hr@empresa.com");
  const [reason, setReason] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [offboardingEvent, setOffboardingEvent] = useState(null);

  const [grantSystemId, setGrantSystemId] = useState("");
  const [grantRole, setGrantRole] = useState("");
  const [grantRisk, setGrantRisk] = useState("low");
  const [grantExternalId, setGrantExternalId] = useState("");
  const [grantSubmitting, setGrantSubmitting] = useState(false);
  const [grantError, setGrantError] = useState(null);

  function loadPerson() {
    setLoading(true);
    api
      .getPerson(personId)
      .then(setPerson)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    loadPerson();
    api.listSystems().then(setSystems).catch(() => {});
  }, [personId]);

  async function handleOffboard(e) {
    e.preventDefault();
    const confirmed = window.confirm(
      `¿Seguro que quieres revocar TODOS los accesos de ${person.full_name}? ` +
        `Esta acción es irreversible.`
    );
    if (!confirmed) return;

    setSubmitting(true);
    setError(null);
    try {
      const event = await api.startOffboarding({
        person_id: personId,
        initiated_by: initiatedBy,
        reason: reason || null,
      });
      setOffboardingEvent(event);
      loadPerson();
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  async function handleAddGrant(e) {
    e.preventDefault();
    setGrantSubmitting(true);
    setGrantError(null);
    try {
      await api.addAccessGrant(personId, {
        system_id: grantSystemId,
        role: grantRole || null,
        risk_level: grantRisk,
        external_account_id: grantExternalId || null,
      });
      setGrantSystemId("");
      setGrantRole("");
      setGrantRisk("low");
      setGrantExternalId("");
      loadPerson();
    } catch (err) {
      setGrantError(err.message);
    } finally {
      setGrantSubmitting(false);
    }
  }

  if (loading) return <p>Cargando persona...</p>;
  if (error) return <p className="error">Error: {error}</p>;
  if (!person) return null;

  const sortedGrants = [...person.access_grants].sort(
    (a, b) => (RISK_ORDER[a.risk_level] ?? 99) - (RISK_ORDER[b.risk_level] ?? 99)
  );

  const canOffboard = person.status !== "offboarded";
  const grantedSystemIds = new Set(person.access_grants.map((g) => g.system_id));
  const availableSystems = systems.filter((s) => !grantedSystemIds.has(s.id));

  return (
    <div>
      <button onClick={onBack}>← Volver a la lista</button>

      <h2>{person.full_name}</h2>
      <p>
        {person.email} · {person.person_type} ·{" "}
        <span className={`status status-${person.status}`}>{person.status}</span>
      </p>

      <h3>Grafo de identidad ({sortedGrants.length} sistemas)</h3>
      {sortedGrants.length === 0 ? (
        <p className="subtitle">Todavía no tiene ningún acceso asignado.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Sistema</th>
              <th>Rol</th>
              <th>Riesgo</th>
              <th>Estado</th>
            </tr>
          </thead>
          <tbody>
            {sortedGrants.map((grant) => (
              <tr key={grant.id}>
                <td>{grant.system_name}</td>
                <td>{grant.role}</td>
                <td>
                  <span className={`risk risk-${grant.risk_level}`}>
                    {grant.risk_level}
                  </span>
                </td>
                <td>{grant.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {canOffboard && availableSystems.length > 0 && (
        <div className="offboard-panel">
          <h3>Asignar acceso</h3>
          <form onSubmit={handleAddGrant}>
            <label>
              Sistema
              <select
                value={grantSystemId}
                onChange={(e) => setGrantSystemId(e.target.value)}
                required
              >
                <option value="">Selecciona un sistema...</option>
                {availableSystems.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Rol
              <input
                type="text"
                value={grantRole}
                onChange={(e) => setGrantRole(e.target.value)}
                placeholder="ej. member, admin, write"
              />
            </label>
            <label>
              Nivel de riesgo
              <select value={grantRisk} onChange={(e) => setGrantRisk(e.target.value)}>
                <option value="low">Bajo</option>
                <option value="medium">Medio</option>
                <option value="high">Alto</option>
                <option value="critical">Crítico</option>
              </select>
            </label>
            <label>
              Identificador en el sistema externo (opcional)
              <input
                type="text"
                value={grantExternalId}
                onChange={(e) => setGrantExternalId(e.target.value)}
                placeholder="ej. su username real en GitHub/AWS"
              />
            </label>

            {grantError && <p className="error">{grantError}</p>}

            <button type="submit" className="primary" disabled={grantSubmitting}>
              {grantSubmitting ? "Añadiendo..." : "Añadir acceso"}
            </button>
          </form>
        </div>
      )}

      {canOffboard && (
        <div className="offboard-panel">
          <h3>Iniciar offboarding</h3>
          <form onSubmit={handleOffboard}>
            <label>
              Iniciado por
              <input
                type="email"
                value={initiatedBy}
                onChange={(e) => setInitiatedBy(e.target.value)}
                required
              />
            </label>
            <label>
              Motivo (opcional)
              <input
                type="text"
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                placeholder="ej. renuncia, despido, fin de contrato"
              />
            </label>
            <button type="submit" className="danger" disabled={submitting}>
              {submitting ? "Procesando..." : "Revocar todos los accesos"}
            </button>
          </form>
        </div>
      )}

      {offboardingEvent && (
        <div className="offboard-result">
          <h3>Resultado del offboarding</h3>
          <p>
            Estado: <strong>{offboardingEvent.status}</strong>
          </p>
          <ul>
            {offboardingEvent.log_entries.map((log, i) => (
              <li key={i} className={log.result === "success" ? "ok" : "fail"}>
                {log.system_name}: {log.result} — {log.detail}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}