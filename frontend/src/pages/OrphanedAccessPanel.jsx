import { useEffect, useState } from "react";
import { api } from "../api/client";

const REASON_LABELS = {
  person_offboarded: "Persona ya offboardeada",
  unknown_identity: "Identidad desconocida",
  no_active_grant_recorded: "Acceso sin registro (en la sombra)",
};

export default function OrphanedAccessPanel() {
  const [findings, setFindings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    api
      .getOrphanedAccess()
      .then(setFindings)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p>Buscando accesos huérfanos...</p>;
  if (error) return <p className="error">Error: {error}</p>;

  return (
    <div>
      <h2>Accesos huérfanos</h2>
      <p className="subtitle">
        Compara quién tiene acceso activo en cada sistema AHORA MISMO
        contra quién debería tenerlo según el grafo de identidad.
      </p>

      {findings.length === 0 ? (
        <p className="ok-message">✅ No se detectaron accesos huérfanos.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Sistema</th>
              <th>Cuenta externa</th>
              <th>Email</th>
              <th>Motivo</th>
            </tr>
          </thead>
          <tbody>
            {findings.map((f, i) => (
              <tr key={i} className={`finding-${f.reason}`}>
                <td>{f.system_name}</td>
                <td>{f.external_account_id}</td>
                <td>{f.email}</td>
                <td>{REASON_LABELS[f.reason] || f.reason}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}